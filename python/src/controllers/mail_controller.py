from flask import jsonify, Response
import base64
import logging
from datetime import datetime, timedelta
from rkdigi import EmailSender
from typing import List, Dict, Any

from utils.config import (
    MAIL_SMTP_SENDER,
    MAIL_SMTP_PASSWORD,
    MAIL_SMTP_PORT,
    MAIL_SMTP_SERVER,
    MAIL_DESC_NEW_TASK_USER,
    MAIL_DESC_NEW_TASK_ANSVARLIG,
    ONBOARDING_BASE_URL,
)
from utils.client_url import get_client_base_url
from models import Mail, MailAttachment, Forløb, Opgave
from utils.db_connection import get_db_client
from utils.access_control import is_current_user_admin
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_

db_client = get_db_client()
logger = logging.getLogger(__name__)


SUBJECT_ANSVARLIG_NEW_TASK = "Ny opgave tildelt i onboardingforløb"


# Helpers

def _to_base64_str(data: str | bytes | bytearray | memoryview | None) -> str | None:
    if data is None:
        return None
    if isinstance(data, str):
        return data
    if isinstance(data, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(data)).decode("ascii")
    raise TypeError(f"Unsupported attachment content type: {type(data)!r}")


def _to_bytes(data: str | bytes | bytearray | memoryview | None) -> bytes | None:
    if data is None:
        return None
    if isinstance(data, (bytes, bytearray, memoryview)):
        return bytes(data)
    if isinstance(data, str):
        # Stored as base64 text in DB
        return base64.b64decode(data)
    raise TypeError(f"Unsupported attachment content type: {type(data)!r}")


def _attachments_for_rkdigi(attachments: list[dict[str, Any]] | None) -> list[tuple[str, bytes]] | None:
    """Convert our attachment dicts to rk-digi EmailSender attachments.

    rk-digi accepts attachments as either file paths (str) or (filename, bytes) tuples.
    Our DB payloads are lists of dicts containing base64 strings or raw bytes.
    """
    if attachments is None:
        return None

    transformed = []
    for attachment in attachments:
        if not attachment:
            continue
        filename = attachment.get("filename") or "attachment"
        content = attachment.get("file_data", attachment.get("content"))
        content_bytes = _to_bytes(content)
        if content_bytes is None:
            raise ValueError("Attachment content is missing")

        transformed.append((filename, content_bytes))
    return transformed


def _split_name(full_name: str) -> tuple[str, str]:
    if not full_name:
        return "", ""
    parts = str(full_name).split()
    if not parts:
        return "", ""
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first_name, last_name


def _is_external_forloeb(forloeb: Forløb) -> bool:
    try:
        return not bool(getattr(forloeb, "userdq", None))
    except Exception:
        return False


def _forloeb_overview_url(forloeb: Forløb, opgave_id: int | None = None, is_forloeb_user: bool = False, force_internal: bool = False) -> str:
    # Per requirement: frontend deep-link expects `id` for ForløbID and `item` for task.
    base_url = get_client_base_url(ONBOARDING_BASE_URL)

    def _append_query_param(url: str, key: str, value: str) -> str:
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}{key}={value}"

    url = f"{base_url}/mit-forloeb" \
          if is_forloeb_user else \
          f"{base_url}/forloeb-overview?id={forloeb.ForløbID}"

    if opgave_id is not None:
        url = _append_query_param(url, "item", str(opgave_id))
    if _is_external_forloeb(forloeb) and not force_internal:
        url = _append_query_param(url, "external", "true")
    return url


def _button_link_html(url: str, text: str) -> str:
    # Keep styling consistent with existing welcome button.
    return (
        f'<a href="{url}" '
        'style="text-decoration: none; background-color: rgb(56, 65, 84); '
        'border: 10px solid rgb(56, 65, 84); color: rgb(237, 229, 220) !important; '
        'cursor: pointer; user-select: none; display: inline-block; margin-bottom: 20px;">'
        f"{text}</a>"
    )


def _format_date(dt: datetime | None) -> str:
    if not dt:
        return ""
    try:
        return dt.strftime("%d/%m-%Y")
    except Exception:
        return str(dt)


def _render_task_blocks_for_forloeb(forloeb: Forløb, opgaver: List[Opgave]) -> str:
    blocks: List[str] = []
    for opgave in opgaver:
        url = _forloeb_overview_url(forloeb, opgave_id=opgave.OpgaveID, is_forloeb_user=True)
        blocks.append(
            "".join(
                [
                    f"<div>- <strong>{opgave.title}</strong></div>\n",
                    f"<div>Start: {_format_date(opgave.startdato)}</div>" if opgave.startdato else "",
                    f"<div>Deadline: {_format_date(opgave.slutdato)}</div>" if opgave.slutdato else "",
                    f"<div style=\"margin-top: 12px;\">{_button_link_html(url, 'Se opgaven i dit onboarding-forløb')}</div>\n",
                ]
            )
        )

    if len(blocks) <= 1:
        return "".join(blocks)
    return "<hr>".join(blocks)


def _render_task_blocks_for_ansvarlig(opgaver: List[Opgave]) -> str:
    blocks: List[str] = []
    for opgave in opgaver:
        forloeb = getattr(opgave, "forløb", None)
        if not forloeb:
            continue
        url = _forloeb_overview_url(forloeb, opgave_id=opgave.OpgaveID, force_internal=True)
        blocks.append(
            "".join(
                [
                    f"<div>- <strong>{opgave.title}</strong></div>\n",
                    f"<div>Medarbejder: {forloeb.name}</div>" if getattr(forloeb, "name", None) else "",
                    f"<div>Start: {_format_date(opgave.startdato)}</div>" if opgave.startdato else "",
                    f"<div>Deadline: {_format_date(opgave.slutdato)}</div>" if opgave.slutdato else "",
                    f"<div style=\"margin-top: 12px;\">{_button_link_html(url, 'Se opgaven i onboarding-forløbet')}</div>\n",
                ]
            )
        )

    if len(blocks) <= 1:
        return "".join(blocks)
    return "<hr>\n".join(blocks)


# Plan and send mail functions

def plan_mail(recipient_email: str, subject: str, message: str, opgave_id: int | None = None, forloeb_id: int | None = None, attachment: dict | None = None, description: str | None = None) -> bool:
    """
    Adds an email to DB to be sent at a later point.

    Parameters:
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        message (str): The body of the email.
        opgave_id (int, optional): The ID of the related Opgave, if applicable.
        forloeb_id (int, optional): The ID of the related Forløb, if applicable.
        attachment (dict, optional): An optional attachment with keys "filename" and "file_data" (base64 string or raw bytes).
        description (str, optional): An optional description to categorize the email ("NEW_TASK_USER" or "NEW_TASK_ANSVARLIG").
    """
    session = db_client.get_session()
    try:
        mail = Mail(
            subject=subject,
            body=message,
            recipient=recipient_email,
            created=datetime.now(),
            OpgaveID=opgave_id,
            ForløbID=forloeb_id,
            description=description,
        )
        session.add(mail)
        session.commit()  # Commit to get MailID

        if attachment is not None:
            # `file_data` is stored and transmitted as base64 text.
            # Sources (e.g. PDF generation) may provide raw bytes.
            attachment_content = attachment.get('content', attachment.get('file_data'))
            file_data_b64 = _to_base64_str(attachment_content)
            if not file_data_b64:
                raise ValueError("Attachment content is missing or empty")
            mail_attachment = MailAttachment(
                filename=attachment['filename'],
                file_data=file_data_b64,
                MailID=mail.MailID  # Link attachment to mail
            )
            session.add(mail_attachment)
            session.commit()

    except Exception as e:
        session.rollback()
        logger.error(f"Error planning email to {recipient_email}: {e}")
        raise e
    else:
        return True
    finally:
        session.close()


def get_planned_mails() -> list[dict[str, Any]] | None:
    session = db_client.get_session()
    try:
        mails = session.query(Mail).filter_by(isSent=False).all()
        session.commit()
        mails_data = []
        for mail in mails:
            # Get attachments for this mail
            attachments = session.query(MailAttachment).filter_by(MailID=mail.MailID).all()
            attachments_data = [
                {
                    "filename": attachment.filename,
                    "file_data": _to_base64_str(attachment.file_data)
                }
                for attachment in attachments
            ]
            mails_data.append({
                "id": mail.MailID,
                "subject": mail.subject,
                "body": mail.body,
                "recipient": mail.recipient,
                "isSent": mail.isSent,
                "attachments": attachments_data
            })
        return mails_data
    except Exception as e:
        logger.error(f"Error fetching planned emails: {e}")
        session.rollback()
        return None
    finally:
        session.close()


def delete_planned_mail(mail_id: int) -> tuple[Response, int]:
    session = db_client.get_session()
    try:
        mail = session.query(Mail).filter_by(MailID=mail_id, isSent=False).first()
        if mail is None:
            return jsonify({"message": "No unsent email found with the provided ID"}), 404
        session.delete(mail)
        session.commit()
        return jsonify({"message": "Planned email deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": "Error deleting planned email", "error": str(e)}), 500
    finally:
        session.close()


def purge_mails(days: int = 30) -> tuple[Response, int]:
    """Delete mails older than the specified number of days."""
    session = db_client.get_session()
    try:
        threshold_date = datetime.now() - timedelta(days=days)
        old_mails = session.query(Mail).filter(Mail.created < threshold_date).all()
        for mail in old_mails:
            session.delete(mail)
        session.commit()
        return jsonify({"message": f"Deleted mails older than {days} days", "deleted_count": len(old_mails)}), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error purging old emails: {e}")
        return jsonify({"message": "Error purging old emails", "error": str(e)}), 500
    finally:
        session.close()


def send_all_mails() -> tuple[Response, int]:
    """
    Fetches all planned mails from DB and attempts to send them. Updates DB status accordingly.
    """
    mails = get_planned_mails()
    if mails is None or len(mails) == 0:
        return jsonify({"message": "No planned emails to send"}), 200

    session = db_client.get_session()
    sent_count = 0
    total_count = len(mails) if mails else 0
    try:
        for mail_dict in mails:
            mail_obj = session.query(Mail).filter_by(MailID=mail_dict.get('id')).first()

            reply_to = None
            if mail_obj is not None and getattr(mail_obj, 'forløb', None) is not None:
                reply_to = getattr(mail_obj.forløb, 'admin', None)

            status = send_mail(
                mail_dict.get('recipient'),
                mail_dict.get('subject'),
                mail_dict.get('body'),
                attachments=mail_dict.get('attachments', None),
                reply_to=reply_to,
            )
            if mail_obj:
                mail_obj.isSent = status
                if status:
                    sent_count += 1
        session.commit()
    except Exception as e:
        session.rollback()
        return jsonify({"message": "Error sending planned emails", "error": str(e)}), 500
    finally:
        session.close()

    return jsonify({"message": "Planned emails sent successfully", "count": total_count, "sent": sent_count}), 200


def send_mail(recipient_email: str | list[str], subject: str, message: str, attachments: list[dict] | None = None, reply_to: str | None = None) -> bool:
    """
    Sends an email via SMTP using rk-digi and the configured SMTP sender.

    Parameters:
        recipient_email (str or list[str]): Email address or list of addresses to send the email to.
        subject (str): The subject of the email.
        message (str): The body of the email.
        attachments (list[dict] | None): Optional list of attachments, each with at least
            "filename" and "file_data" (base64-encoded string). Defaults to None.
        reply_to (str | None): Optional reply-to email address to set on the message.
    """
    try:
        if not MAIL_SMTP_SERVER or not MAIL_SMTP_SENDER or not MAIL_SMTP_PASSWORD:
            raise ValueError("SMTP configuration is incomplete. Check environment variables.")

        email_sender = EmailSender(
            smtp_server=MAIL_SMTP_SERVER,
            smtp_port=MAIL_SMTP_PORT,
            sender_email=MAIL_SMTP_SENDER,
            sender_password=MAIL_SMTP_PASSWORD,
            sender_name="Randers Kommune Onboarding",
            reply_to_email=reply_to
        )
        email_sender.send_email(
            recipients=recipient_email,
            subject=subject,
            body=message,
            attachments=_attachments_for_rkdigi(attachments),
        )
        return True
    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {e}")
        return False


# Helper function to create email content from a template with placeholders replaced by context values

def compose_mail_content(template: str, context: dict[str, Any]) -> str:
    """
    Composes email content by replacing placeholders in the template with values from the context.
    Adds <html> tags around the content to ensure proper formatting in HTML emails.

    Parameters:
        template (str): The email template containing placeholders in the format {placeholder}.
        context (dict): A dictionary mapping placeholder names to their replacement values.

    Returns:
        str: The composed email content with placeholders replaced by context values.
    """
    if not template or not context:
        return template

    content = template
    for key, value in context.items():
        placeholder = f"{{{key}}}"
        content = content.replace(placeholder, str(value) if value is not None else "")

    content = content.replace("\n", "<br>")  # Convert newlines to HTML line breaks
    return f"<html>{content}</html>"


def _send_new_tasks_mail_to_forloeb(forloeb: Forløb, opgaver: List[Opgave]) -> bool:
    first_name, _last_name = _split_name(getattr(forloeb, "name", ""))
    context = {
        "navn": first_name,
        "tasks": _render_task_blocks_for_forloeb(forloeb, opgaver),
    }

    subject = "Nye opgaver på dit onboarding-forløb"
    template = (
        "Kære {navn},\n\n"
        "Der er blevet tilføjet nye opgaver til dit onboarding-forløb.\n\n"
        "{tasks}\n"
        "Med venlig hilsen,\n"
        "Randers Kommune"
    )
    body = compose_mail_content(template, context)
    return send_mail(forloeb.usermail, subject, body, reply_to=getattr(forloeb, "admin", None))


def _send_new_tasks_mail_to_ansvarlig(ansvarlig_email: str, opgaver: List[Opgave]) -> bool:
    context = {
        "tasks": _render_task_blocks_for_ansvarlig(opgaver),
    }

    subject = "Nye opgaver tildelt i onboardingmodulet"
    template = (
        "Kære kollega,\n\n"
        "Du er blevet tildelt som ansvarlig på nye opgaver i onboardingmodulet.\n\n"
        "{tasks}\n"
        "Med venlig hilsen,\n"
        "Randers Kommune"
    )
    body = compose_mail_content(template, context)
    return send_mail(ansvarlig_email, subject, body)


def send_planned_new_tasks_notifications() -> tuple[Response, int]:
    """Cron: Send consolidated 'new task' notifications based on planned Mail rows.

    This cron consumes planned Mail rows of two types:
    - Mail.description == NEW_TASK_USER: queued for Forløb.usermail
    - Mail.description == NEW_TASK_ANSVARLIG: queued for Opgave.ansvarligEmail

    Legacy support:
    - If description is NULL but subject matches SUBJECT_ANSVARLIG_NEW_TASK, it is treated as NEW_TASK_ANSVARLIG.
    """
    session = db_client.get_session()
    try:
        planned = (
            session.query(Mail)
            .options(selectinload(Mail.opgave).selectinload(Opgave.forløb))
            .filter(
                Mail.isSent.is_(False),
                Mail.OpgaveID.is_not(None),
                or_(
                    Mail.description.in_([MAIL_DESC_NEW_TASK_USER, MAIL_DESC_NEW_TASK_ANSVARLIG]),
                    and_(Mail.description.is_(None), Mail.subject == SUBJECT_ANSVARLIG_NEW_TASK),
                ),
            )
            .all()
        )

        if not planned:
            return jsonify({"message": "No planned new-task emails to process"}), 200

        planned_user: List[Mail] = []
        planned_ansvarlig: List[Mail] = []
        for mail in planned:
            desc = getattr(mail, "description", None)
            if desc == MAIL_DESC_NEW_TASK_USER:
                planned_user.append(mail)
            elif desc == MAIL_DESC_NEW_TASK_ANSVARLIG or (desc is None and mail.subject == SUBJECT_ANSVARLIG_NEW_TASK):
                planned_ansvarlig.append(mail)

        # USER mails: 1 per Forløb
        user_forloeb_to_mails: Dict[int, List[Mail]] = {}
        for mail in planned_user:
            opgave = getattr(mail, "opgave", None)
            forloeb = getattr(opgave, "forløb", None) if opgave else None
            if not forloeb or not getattr(forloeb, "ForløbID", None):
                continue
            user_forloeb_to_mails.setdefault(forloeb.ForløbID, []).append(mail)

        # ANSVARLIG mails: 1 per recipient email
        ansvarlig_to_mails: Dict[str, List[Mail]] = {}
        for mail in planned_ansvarlig:
            recipient = (getattr(mail, "recipient", None) or "").strip().lower()
            if not recipient:
                continue
            ansvarlig_to_mails.setdefault(recipient, []).append(mail)

        now = datetime.now()
        marked_sent_user = 0
        marked_sent_ansvarlig = 0

        for forloeb_id, mails in user_forloeb_to_mails.items():
            opgaver_by_id: Dict[int, Opgave] = {}
            forloeb_obj = None
            for mail in mails:
                opgave = getattr(mail, "opgave", None)
                if not opgave:
                    continue
                opgaver_by_id[opgave.OpgaveID] = opgave
                if forloeb_obj is None:
                    forloeb_obj = getattr(opgave, "forløb", None)

            if not forloeb_obj or not getattr(forloeb_obj, "usermail", None):
                continue

            if _send_new_tasks_mail_to_forloeb(forloeb_obj, list(opgaver_by_id.values())):
                for mail in mails:
                    mail.isSent = True
                    mail.sent = now
                    marked_sent_user += 1

        for recipient, mails in ansvarlig_to_mails.items():
            opgaver_by_id: Dict[int, Opgave] = {}
            for mail in mails:
                opgave = getattr(mail, "opgave", None)
                if not opgave:
                    continue
                opgaver_by_id[opgave.OpgaveID] = opgave

            if _send_new_tasks_mail_to_ansvarlig(recipient, list(opgaver_by_id.values())):
                for mail in mails:
                    mail.isSent = True
                    mail.sent = now
                    marked_sent_ansvarlig += 1

        session.commit()
        return (
            jsonify(
                {
                    "message": "Processed planned new-task notifications",
                    "planned_count": len(planned),
                    "forloeb_count": len(user_forloeb_to_mails),
                    "ansvarlig_count": len(ansvarlig_to_mails),
                    "marked_sent_user": marked_sent_user,
                    "marked_sent_ansvarlig": marked_sent_ansvarlig,
                }
            ),
            200,
        )
    except Exception as e:
        session.rollback()
        logger.error(f"Error processing planned new-task emails: {e}")
        return jsonify({"message": "Error processing planned new-task emails", "error": str(e)}), 500
    finally:
        session.close()


def create_mail_ansvarlig(opgave: Opgave) -> tuple[str, str]:
    subject = SUBJECT_ANSVARLIG_NEW_TASK
    ansvarlig_navn = getattr(opgave, "ansvarlig", "")
    booking = getattr(opgave, "booking", None)
    booking_line = f"Kalenderbooking: {_format_date(booking)}\n" if booking else ""

    context = {
        "ansvarlig": ansvarlig_navn,
        "opgave": getattr(opgave, "title", ""),
        "note": getattr(opgave, "note", "") or "",
        "slutdato": _format_date(getattr(opgave, "slutdato", None)),
        "booking": booking_line,
        "link": _button_link_html(
            "http://onboarding.data.randers.dk/ansvarlig-overview",
            "Se opgaven under 'Mine ansvar'",
        ),
    }

    template = (
        "Kære {ansvarlig},\n\n"
        "Du er blevet tildelt en ny opgave: {opgave}.\n"
        "Du er ansvarlig for opgaven og skal hjælpe den nye medarbejder med at løse denne.\n\n"
        "{note}\n"
        "Deadline: {slutdato}.\n"
        "{booking}"
        "{link}\n\n"
        "Med venlig hilsen,\n"
        "Randers Kommune"
    )

    # Only show note block if present
    if context["note"]:
        context["note"] = f"Note til ansvarlig: {context['note']}"
    body = compose_mail_content(template, context)
    return subject, body


def create_mail_new_task_user(forloeb: Forløb, opgave: Opgave) -> tuple[str, str]:
    first_name, _last_name = _split_name(getattr(forloeb, "name", ""))
    context = {
        "navn": first_name,
        "tasks": _render_task_blocks_for_forloeb(forloeb, [opgave]),
    }

    subject = "Ny opgave på dit onboarding-forløb"
    template = (
        "Kære {navn},\n\n"
        "Der er blevet tilføjet en ny opgave til dit onboarding-forløb.\n\n"
        "{tasks}\n"
        "Med venlig hilsen,\n"
        "Randers Kommune"
    )
    body = compose_mail_content(template, context)
    return subject, body


def create_mail_external_access(forloeb: Forløb, link: str, expires_at) -> tuple[str, str]:
    first_name, _last_name = _split_name(getattr(forloeb, "name", ""))
    try:
        expires_str = expires_at.astimezone(None).strftime('%d/%m %H:%M')
    except Exception:
        expires_str = str(expires_at)

    context = {
        "navn": first_name,
        "expires": expires_str,
        "link": _button_link_html(link, "Åbn onboarding-forløb"),
    }
    subject = "Midlertidig adgang til onboardingforløb"
    template = (
        "Kære {navn},\n\n"
        "Du har anmodet om midlertidig adgang til dit onboardingforløb.\n\n"
        "Linket udløber {expires}.\n\n"
        "{link}\n\n"
        "Hvis du ikke selv har anmodet om dette link, kan du ignorere mailen.\n\n"
        "Med venlig hilsen,\n"
        "Randers Kommune"
    )
    body = compose_mail_content(template, context)
    return subject, body


def compose_welcome_mail(forloeb: Forløb, custom_message: str) -> str:
    if not isinstance(forloeb, Forløb):
        raise TypeError(f"compose_welcome_mail expects Forløb, got {type(forloeb)!r}")

    name = getattr(forloeb, "name", "")
    startdate = getattr(forloeb, "startdate", None)
    enddate = getattr(forloeb, "enddate", None)
    url = _forloeb_overview_url(forloeb)

    first_name, last_name = _split_name(name)
    context = {
        "navn": first_name,
        "efternavn": last_name,
        "link": _button_link_html(url, "Se dit onboarding-forløb"),
        "startdato": _format_date(startdate),
        "slutdato": _format_date(enddate),
    }
    return compose_mail_content(custom_message, context)


def send_welcome_mail(forloeb_id: int, subject: str, custom_message: str) -> tuple[Response, int]:
    """
    Composes and sends a welcome email to the user associated with the given forløb ID, using the provided custom message template.

    Parameters:
        forloeb_id (int): The ID of the forløb to send the welcome
        custom_message (str): The email template containing placeholders to be replaced with forløb-specific information.
    """
    try:
        forloeb_id_int = int(forloeb_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid forløb ID format. Must be an integer."}), 400

    if not custom_message or not isinstance(custom_message, str):
        return jsonify({"message": "Custom message must be a non-empty string.", "custom_message": custom_message}), 400

    if not subject or not isinstance(subject, str):
        return jsonify({"message": "Subject must be a non-empty string."}), 400

    if not is_current_user_admin():
        return jsonify({"error": "Forbidden"}), 403

    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id_int).first()
        if not forloeb:
            return jsonify({"message": f"Forløb with ID {forloeb_id} not found."}), 404

        mail_content = compose_welcome_mail(forloeb, custom_message)
        if mail_content:
            res = send_mail(forloeb.usermail, subject, mail_content, reply_to=forloeb.admin)
            if res:
                return jsonify({"message": "Welcome mail sent successfully", "recipient": forloeb.usermail}), 200
            else:
                return jsonify({"message": "Failed to send welcome mail", "recipient": forloeb.usermail}), 500
        else:
            return jsonify({"message": "Failed to compose welcome mail", "recipient": forloeb.usermail}), 500
    finally:
        session.close()


def notify_expired_tasks_aggregated() -> tuple[Response, int]:
    """Cron: Send consolidated notifications for expired tasks (repeat reminders)."""
    session = db_client.get_session()
    try:
        now = datetime.now()
        opgaver = (
            session.query(Opgave)
            .options(selectinload(Opgave.forløb))
            .filter(Opgave.slutdato <= now, Opgave.result.is_(False), Opgave.ForløbID.is_not(None))
            .all()
        )

        if not opgaver:
            return jsonify({"message": "No expired tasks to notify"}), 200

        forloeb_to_opgaver: Dict[int, Dict[int, Opgave]] = {}
        ansvarlig_to_opgaver: Dict[str, Dict[int, Opgave]] = {}

        for opgave in opgaver:
            forloeb = getattr(opgave, "forløb", None)
            if not forloeb:
                continue

            forloeb_to_opgaver.setdefault(forloeb.ForløbID, {})[opgave.OpgaveID] = opgave
            ansvarlig_email = (getattr(opgave, "ansvarligEmail", None) or "").strip().lower()
            if ansvarlig_email:
                ansvarlig_to_opgaver.setdefault(ansvarlig_email, {})[opgave.OpgaveID] = opgave

        sent_user = 0
        sent_ansvarlig = 0

        for forloeb_id, opgaver_by_id in forloeb_to_opgaver.items():
            any_opgave = next(iter(opgaver_by_id.values()), None)
            forloeb = getattr(any_opgave, "forløb", None) if any_opgave else None
            if not forloeb or not getattr(forloeb, "usermail", None):
                continue

            first_name, _last_name = _split_name(getattr(forloeb, "name", ""))
            context = {
                "navn": first_name,
                "efternavn": _last_name,
                "tasks": _render_task_blocks_for_forloeb(forloeb, list(opgaver_by_id.values())),
            }
            subject = "Overskredne opgaver på dit onboarding-forløb"
            template = (
                "Kære {navn},\n\n"
                "Du har én eller flere opgaver på dit onboarding-forløb hvor deadline er overskredet.\n\n"
                "{tasks}\n"
                "Med venlig hilsen,\n"
                "Randers Kommune"
            )
            body = compose_mail_content(template, context)
            if send_mail(forloeb.usermail, subject, body, reply_to=getattr(forloeb, "admin", None)):
                sent_user += 1

        for ansvarlig_email, opgaver_by_id in ansvarlig_to_opgaver.items():
            context = {
                "tasks": _render_task_blocks_for_ansvarlig(list(opgaver_by_id.values())),
            }
            subject = "Overskredne opgaver i onboardingforløb"
            template = (
                "Kære kollega,\n\n"
                "Du er ansvarlig for én eller flere opgaver hvor deadline er overskredet.\n\n"
                "{tasks}\n"
                "Med venlig hilsen,\n"
                "Randers Kommune"
            )
            body = compose_mail_content(template, context)
            if send_mail(ansvarlig_email, subject, body):
                sent_ansvarlig += 1

        return (
            jsonify(
                {
                    "message": "Expired task notifications sent",
                    "expired_task_count": len(opgaver),
                    "forloeb_count": len(forloeb_to_opgaver),
                    "ansvarlig_count": len(ansvarlig_to_opgaver),
                    "sent_user": sent_user,
                    "sent_ansvarlig": sent_ansvarlig,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error notifying expired tasks: {e}")
        return jsonify({"message": "Error notifying expired tasks", "error": str(e)}), 500
    finally:
        session.close()

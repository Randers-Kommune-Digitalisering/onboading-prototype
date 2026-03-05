from flask import jsonify
import base64
import logging
from datetime import datetime
from rkdigi import EmailSender

from utils.config import MAIL_SMTP_SENDER, MAIL_SMTP_PASSWORD, MAIL_SMTP_PORT, MAIL_SMTP_SERVER
from models import Mail, MailAttachment, Forløb
from utils.db_connection import get_db_client

db_client = get_db_client()
logger = logging.getLogger(__name__)


# Helpers

def _to_base64_str(data):
    if data is None:
        return None
    if isinstance(data, str):
        return data
    if isinstance(data, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(data)).decode("ascii")
    raise TypeError(f"Unsupported attachment content type: {type(data)!r}")


def _to_bytes(data):
    if data is None:
        return None
    if isinstance(data, (bytes, bytearray, memoryview)):
        return bytes(data)
    if isinstance(data, str):
        # Stored as base64 text in DB
        return base64.b64decode(data)
    raise TypeError(f"Unsupported attachment content type: {type(data)!r}")


def _attachments_for_rkdigi(attachments):
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


# Plan and send mail functions

def plan_mail(recipient_email, subject, message, opgave_id=None, forloeb_id=None, attachment=None):
    """
    Adds an email to DB to be sent at a later point.

    Parameters:
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        message (str): The body of the email.
        opgave_id (int, optional): The ID of the related Opgave, if applicable.
        forloeb_id (int, optional): The ID of the related Forløb, if applicable.
        attachment (dict, optional): An optional attachment with keys "filename" and "file_data" (base64 string or raw bytes).
    """
    session = db_client.get_session()
    try:
        mail = Mail(
            subject=subject,
            body=message,
            recipient=recipient_email,
            created=datetime.now(),
            OpgaveID=opgave_id,
            ForløbID=forloeb_id
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


def get_planned_mails():
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


def send_all_mails():
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


def send_mail(recipient_email, subject, message, attachments=None, reply_to=None):
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
            # attachments=_attachments_for_rkdigi(attachments),
        )
        return True
    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {e}")
        return False


# Helper function to create email content from a template with placeholders replaced by context values

def compose_mail_content(template, context):
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


# Welcome mails

def compose_welcome_mail(forloeb, custom_message):
    forloeb = {
        "id": forloeb.ForløbID,
        "name": forloeb.name,
        "userdq": forloeb.userdq,
        "startdate": forloeb.startdate,
        "slutdate": forloeb.enddate
    }
    link = f"http://onboarding.data.randers.dk/forloeb-overview?forloebId={forloeb['id']}"
    if forloeb.get('userdq') is None:
        link += "&external=true"

    context = {
        "navn": forloeb['name'].split()[0] if forloeb.get('name') else '',
        "efternavn": " ".join(forloeb['name'].split()[1:]) if forloeb.get('name') and len(forloeb['name'].split()) > 1 else '',
        "link": f'<a href="{link}" style="text-decoration: none; background-color: rgb(56, 65, 84); border: 10px solid  rgb(56, 65, 84); color: rgb(237, 229, 220) !important; cursor: pointer; user-select: none; display: inline-block; margin-bottom: 20px;">Se dit onboarding-forløb</a>',
        "startdato": forloeb['startdate'].strftime('%d/%m %Y') if forloeb.get('startdate') else '',
        "slutdato": forloeb['slutdate'].strftime('%d/%m %Y') if forloeb.get('slutdate') else '',
        "forløb": forloeb['name'],
    }
    return compose_mail_content(custom_message, context)


def send_welcome_mail(forloeb_id, subject, custom_message):
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

    session = db_client.get_session()
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

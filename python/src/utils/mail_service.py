from flask import jsonify
import base64
import logging
from datetime import datetime, timedelta
from rkdigi import EmailSender

from utils.config import MAIL_SMTP_SENDER, MAIL_SMTP_PASSWORD, MAIL_SMTP_PORT, MAIL_SMTP_SERVER
from models import Mail, MailAttachment
from utils.db_connection import get_db_client
from utils.pdf import create_pdf

db_client = get_db_client()
logger = logging.getLogger(__name__)


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


def plan_mail(recipient_email, subject, message, opgave_id=None, forloeb_id=None, attachment=None):
    """
    Adds an email to DB to be sent at a later point.
    Parameters:
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        message (str): The body of the email.
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
    mails = get_planned_mails()
    if mails is None or len(mails) == 0:
        return jsonify({"message": "No planned emails to send"}), 200

    session = db_client.get_session()
    sent_count = 0
    total_count = len(mails) if mails else 0
    try:
        for mail_dict in mails:
            status = send_mail(
                mail_dict.get('recipient'),
                mail_dict.get('subject'),
                mail_dict.get('body'),
                attachments=mail_dict.get('attachments', None),
                reply_to=mail_dict.get('forløb', {}).get('admin', None)
            )
            # Fetch the actual Mail ORM object
            mail_obj = session.query(Mail).filter_by(MailID=mail_dict.get('id')).first()
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
    Sends an email via SMTP using rk-digi.
    Parameters:
        sender_email (str): The sender's email address.
        subject (str): The subject of the email.
        message (str): The body of the email.
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


def create_mail_ansvarlig(new_opgave):
    new_opgave = {
        "ansvarlig": new_opgave.ansvarlig,
        "title": new_opgave.title,
        "slutdato": new_opgave.slutdato,
        "booking": new_opgave.booking
    }
    subject = "Ny opgave tildelt i onboardingforløb"
    message = (
        f"Hej {new_opgave['ansvarlig']},\n\n" +
        f"Du er blevet tildelt en ny opgave: {new_opgave['title']}.\n" +
        "Du er ansvarlig for opgaven, og skal derfor hjælpe den nye medarbejder med at løse denne.\n\n" +
        (f"Note til ansvarlig: {new_opgave.get('note')}.\n" if new_opgave.get('note') else "") +
        f"Opgaven har deadline d. {new_opgave['slutdato'].strftime('%d/%m %H:%M')}.\n" +
        (f"Der er registret en kalenderbooking d. {new_opgave['booking'].strftime('%d/%m %H:%M')}.\n" if new_opgave['booking'] is not None else '') +
        "Du kan se opgaven under 'Mine ansvar' i onboardingmodulet: http://onboarding.data.randers.dk/ansvarlig-overview.\n" +
        "\nVenlig hilsen,\nRanders Kommune"
    )
    return subject, message


def create_mail_external_access(forloeb, link: str, expires_at):
    subject = "Midlertidig adgang til onboardingforløb"
    try:
        expires_str = expires_at.astimezone(None).strftime('%d/%m %H:%M')
    except Exception:
        expires_str = str(expires_at)

    message = (
        f"Hej {forloeb.name}," + "\n\n" +
        "Du har anmodet om midlertidig adgang til dit onboardingforløb.\n\n"
        f"Åbn forløbet her (linket udløber {expires_str}):\n{link}\n\n"
        "Hvis du ikke selv har anmodet om dette link, kan du ignorere mailen.\n\n"
        "Venlig hilsen\nRanders Kommune"
    )
    return subject, message


def create_mail_expired_ansvarlig(opgave):
    opgave = {
        "ansvarlig": opgave.ansvarlig,
        "title": opgave.title,
        "slutdato": opgave.slutdato,
        "booking": opgave.booking
    }
    subject = "Deadline overskredet for opgave i onboardingforløb"
    message = (
        f"Hej {opgave['ansvarlig']},\n\n" +
        f"Du er ansvarlig for en opgave der er overskredet: {opgave['title']}.\n" +
        "Vær opmærksom at opgaven skal markeres som genneført i onboardingmodulet.\n\n" +
        f"Opgaven havde deadline d. {opgave['slutdato'].strftime('%d/%m %H:%M')}.\n" +
        "\nVenlig hilsen,\nRanders Kommune"
    )
    return subject, message


def create_mail_expired(forloeb, opgave):
    forloeb = {
        "userdq": forloeb.userdq,
        "name": forloeb.name
    }
    opgave = {
        "ansvarlig": opgave.ansvarlig,
        "title": opgave.title,
        "slutdato": opgave.slutdato,
        "booking": opgave.booking
    }
    subject = "Deadline overskredet for opgave i onboardingforløb"
    message = (
        f"Hej {forloeb['name']}," + "\n\n" +
        f"Du har en opgave fra dit onboardingforløb som er overskredet: {opgave['title']}.\n" +
        "Vær opmærksom at opgaven skal markeres som genneført i onboardingmodulet" +
        (f" af den ansvarlige medarbejder {opgave['ansvarlig']}." if opgave['ansvarlig'] is not None else ", og at det er dit ansvar at gøre dette.") + "\n\n" +
        f"Opgaven havde deadline d. {opgave['slutdato'].strftime('%d/%m %H:%M')}.\n" +
        "\nVenlig hilsen,\nRanders Kommune"
    )
    return subject, message


def create_mail_forloeb_start(forloeb):
    forloeb = {
        "id": forloeb.ForløbID,
        "name": forloeb.name,
        "userdq": forloeb.userdq,
        "startdate": forloeb.startdate
    }
    subject = "Dit onboardingforløb er startet"
    pdf = create_pdf(forloeb['id'])
    attachment = {"filename": "onboarding_forloeb.pdf", "content": pdf}
    message = str(
        f"Hej {forloeb['name']}," + "\n\n" +
        "Velkommen til Randers Kommune! Dit onboardingforløb er nu startet." + "\n\n" +
        "Du kan se et overblik over dit forløb i den vedhæftede PDF-fil.\n" +
        "Du kan også tilgå dit forløbet her: http://onboarding.data.randers.dk/ - kræver login med din medarbejderkonto.\n" +
        "\nVenlig hilsen,\nRanders Kommune"
    )
    return subject, message, attachment


def delete_planned_mail(mail_id):
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


def purge_mails(days=30):
    """
    Deletes emails older than the specified number of days.
    Parameters:
        days (int): The age in days beyond which emails should be deleted.
    """
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

import requests
from utils.config import MAIL_SERVICE_URL, MAIL_SERVICE_SENDER
from models import Mail
from utils.db_connection import get_db_client
import datetime

db_client = get_db_client()


def plan_mail(recipient_email, subject, message):
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
            created=datetime.now()
        )
        session.add(mail)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    return True


def send_all_mails():
    session = db_client.get_session()
    try:
        mails = session.query(Mail).all()
        for mail in mails:
            status = send_mail(mail.recipient, mail.subject, mail.body)
            mail.isSent = status in [True]
            session.add(mail)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def send_mail(recipient_email, subject, message):
    """
    Sends an email via an API request.
    Parameters:
        sender_email (str): The sender's email address.
        subject (str): The subject of the email.
        message (str): The body of the email.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "from": MAIL_SERVICE_SENDER,
        "to": recipient_email,
        "title": subject,
        "body": message
    }

    try:
        response = requests.post(MAIL_SERVICE_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def create_mail_ansvarlig(new_opgave):
    new_opgave = {
        "ansvarlig": new_opgave.ansvarlig,
        "title": new_opgave.title,
        "slutdato": new_opgave.slutdato,
        "booking": new_opgave.booking
    }
    subject = "Ny opgave tildelt i onboardingforløb"
    message = (
        f"Hej {new_opgave['ansvarlig']}," + "\n\n" +
        f"Du er blevet tildelt en ny opgave: {new_opgave['title']}." + "\n" +
        "Du er ansvarlig for opgaven, og skal derfor hjælpe den nye medarbejder med at løse denne." + "\n\n" +
        f"Opgaven har deadline d. {new_opgave['slutdato'].strftime('%d/%m %H:%M')}." + "\n" +
        (f"Der er registret en kalenderbooking d. {new_opgave['booking'].strftime('%d/%m %H:%M')}" + ".\n" if new_opgave['booking'] is not None else "") +
        "\nVenlig hilsen,\nPersonale og HR"
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
        f"Hej {opgave['ansvarlig']}," + "\n\n" +
        f"Du er ansvarlig for en opgave der er overskredet: {opgave['title']}." + "\n" +
        "Vær opmærksom at opgaven skal markeres som genneført i onboardingmodulet." + "\n\n" +
        f"Opgaven havde deadline d. {opgave['slutdato'].strftime('%d/%m %H:%M')}." + "\n" +
        "\nVenlig hilsen,\nPersonale og HR"
    )
    return subject, message


def create_mail_expired(forloeb, opgave):
    forloeb = {
        "userdq": forloeb.userdq,
    }
    opgave = {
        "ansvarlig": opgave.ansvarlig,
        "title": opgave.title,
        "slutdato": opgave.slutdato,
        "booking": opgave.booking
    }
    subject = "Deadline overskredet for opgave i onboardingforløb"
    message = (
        f"Hej {forloeb['userdq']}," + "\n\n" +
        f"Du har en opgave fra dit onboardingforløb som er overskredet: {opgave['title']}." + "\n" +
        "Vær opmærksom at opgaven skal markeres som genneført i onboardingmodulet" +
        (f" af den ansvarlige medarbejder {opgave['ansvarlig']}." if opgave['ansvarlig'] is not None else ", og at det er dit ansvar at gøre dette.") + "\n\n" +
        f"Opgaven havde deadline d. {opgave['slutdato'].strftime('%d/%m %H:%M')}." + "\n" +
        "\nVenlig hilsen,\nPersonale og HR"
    )
    return subject, message

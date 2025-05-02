import requests
from utils.config import MAIL_SERVICE_URL, MAIL_SERVICE_SENDER


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
        "subject": subject,
        "text": message
    }

    try:
        response = requests.post(MAIL_SERVICE_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

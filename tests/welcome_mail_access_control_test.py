from unittest.mock import MagicMock, patch

from flask import Flask

from controllers import mail_controller
from models import Forløb


def test_send_welcome_mail_denies_non_admin_and_skips_db():
    app = Flask(__name__)
    app.secret_key = "test"

    with app.test_request_context(
        "/api/forloeb/1/send-welcome",
        method="POST",
        headers={"roles": "User", "usermail": "user@example.com"},
    ):
        with patch.object(mail_controller.db_client, "get_session") as get_session:
            resp, status = mail_controller.send_welcome_mail(1, "s", "m")

    assert status == 403
    assert resp.get_json()["error"] == "Forbidden"
    get_session.assert_not_called()


def test_send_welcome_mail_allows_admin_and_sends():
    app = Flask(__name__)
    app.secret_key = "test"

    forloeb = Forløb()
    forloeb.ForløbID = 1
    forloeb.usermail = "target@example.com"
    forloeb.admin = "admin@example.com"
    forloeb.name = "A B"
    forloeb.startdate = None
    forloeb.enddate = None

    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = forloeb

    with app.test_request_context(
        "/api/forloeb/1/send-welcome",
        method="POST",
        headers={"roles": "Admin", "usermail": "admin@example.com"},
    ):
        with patch.object(mail_controller.db_client, "get_session", return_value=session):
            with patch.object(mail_controller, "compose_welcome_mail", return_value="body"):
                with patch.object(mail_controller, "send_mail", return_value=True) as send_mail:
                    resp, status = mail_controller.send_welcome_mail(1, "subject", "template")

    assert status == 200
    payload = resp.get_json()
    assert payload["message"] == "Welcome mail sent successfully"
    assert payload["recipient"] == "target@example.com"
    send_mail.assert_called_once()

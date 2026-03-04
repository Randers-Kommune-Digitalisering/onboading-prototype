from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from flask import Flask

from controllers import external_access_controller
from models import Forløb


def _make_session_with_forloeb(forloeb: Forløb):
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = forloeb
    return session


def test_request_external_access_cooldown_skips_resend():
    app = Flask(__name__)

    fixed_now = datetime(2026, 3, 4, 12, 0, 0, tzinfo=timezone.utc)

    # Existing unexpired key issued 30 seconds ago -> within 1 minute cooldown.
    forloeb = Forløb()
    forloeb.ForløbID = 123
    forloeb.usermail = "user@example.com"
    forloeb.admin = "admin@example.com"
    forloeb.external_access_key_hash = "deadbeef"
    forloeb.external_access_expires_at = (fixed_now + timedelta(minutes=59, seconds=30)).replace(tzinfo=None)

    session = _make_session_with_forloeb(forloeb)

    with app.test_request_context(
        "/api/external/request-access",
        method="POST",
        json={"forloebId": 123},
        base_url="http://localhost",
    ):
        with patch.object(external_access_controller, "_utc_now", return_value=fixed_now):
            with patch.object(external_access_controller.db_client, "get_session", return_value=session):
                with patch.object(external_access_controller, "create_mail_external_access") as create_mail:
                    with patch.object(external_access_controller, "send_mail") as send_mail:
                        resp, status = external_access_controller.request_external_access()

    assert status == 200
    assert resp.get_json()["message"] == "If the forløb exists, an email has been sent."
    send_mail.assert_not_called()
    create_mail.assert_not_called()
    session.commit.assert_not_called()


def test_request_external_access_after_cooldown_sends_email():
    app = Flask(__name__)

    fixed_now = datetime(2026, 3, 4, 12, 0, 0, tzinfo=timezone.utc)

    # Existing unexpired key issued 2 minutes ago -> cooldown elapsed.
    # issuance_time = fixed_now - 2 minutes -> expiry = issuance + 1 hour
    forloeb = Forløb()
    forloeb.ForløbID = 123
    forloeb.usermail = "user@example.com"
    forloeb.admin = "admin@example.com"
    forloeb.external_access_key_hash = "deadbeef"
    forloeb.external_access_expires_at = (fixed_now + timedelta(minutes=58)).replace(tzinfo=None)

    session = _make_session_with_forloeb(forloeb)

    with app.test_request_context(
        "/api/external/request-access",
        method="POST",
        json={"forloebId": 123},
        base_url="http://localhost",
    ):
        with patch.object(external_access_controller, "_utc_now", return_value=fixed_now):
            with patch.object(external_access_controller.db_client, "get_session", return_value=session):
                with patch.object(external_access_controller, "create_mail_external_access", return_value=("s", "m")):
                    with patch.object(external_access_controller, "send_mail", return_value=True) as send_mail:
                        resp, status = external_access_controller.request_external_access()

    assert status == 200
    assert resp.get_json()["message"] == "If the forløb exists, an email has been sent."
    assert send_mail.call_count == 1
    assert session.commit.call_count == 1

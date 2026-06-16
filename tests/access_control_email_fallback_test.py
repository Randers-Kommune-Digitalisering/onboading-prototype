from flask import Flask, session

from utils.access_control import get_current_user_email


def test_get_current_user_email_falls_back_to_header_only_without_session_user():
    app = Flask(__name__)
    app.secret_key = "test"

    with app.test_request_context("/", headers={"usermail": "Header@Example.com"}):
        assert get_current_user_email() == "header@example.com"


def test_get_current_user_email_does_not_fall_back_to_header_when_session_user_present():
    app = Flask(__name__)
    app.secret_key = "test"

    with app.test_request_context("/", headers={"usermail": "spoof@example.com"}):
        # Simulate a Keycloak-enabled deployment where authentication has created
        # a server-side session user dict, but userinfo lacks an email field.
        session["user"] = {"resource_access": {}}

        assert get_current_user_email() is None

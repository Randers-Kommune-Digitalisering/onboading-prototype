from unittest.mock import MagicMock, patch

from flask import Flask

from controllers import ressource_controller
from models import Opgave, Opgaveskabelon, Ressource


def _make_session(*, opgave: Opgave | None = None, opgaveskabelon: Opgaveskabelon | None = None):
    session = MagicMock()

    opgave_query = MagicMock()
    opgave_query.filter_by.return_value.first.return_value = opgave

    opgaveskabelon_query = MagicMock()
    opgaveskabelon_query.filter_by.return_value.first.return_value = opgaveskabelon

    ressource_query = MagicMock()
    ressource_query.filter_by.return_value.first.return_value = None

    def query_side_effect(model):
        if model is Opgave:
            return opgave_query
        if model is Opgaveskabelon:
            return opgaveskabelon_query
        if model is Ressource:
            return ressource_query
        return MagicMock()

    session.query.side_effect = query_side_effect
    return session


def test_create_ressource_denies_when_not_admin_and_not_ansvarlig():
    app = Flask(__name__)

    opgave = Opgave()
    opgave.OpgaveID = 1
    opgave.ansvarligEmail = "ansvarlig@example.com"

    session = _make_session(opgave=opgave)

    with app.test_request_context(
        "/api/ressource",
        method="POST",
        json={"name": "R", "url": "https://example.com", "OpgaveID": 1},
        headers={"usermail": "other@example.com", "roles": "User"},
    ):
        with patch.object(ressource_controller.db_client, "get_session", return_value=session):
            resp, status = ressource_controller.create_ressource()

    assert status == 403
    assert resp.get_json()["error"] == "Forbidden"


def test_create_ressource_allows_ansvarlig():
    app = Flask(__name__)

    opgave = Opgave()
    opgave.OpgaveID = 2
    opgave.ansvarligEmail = "ansvarlig@example.com"

    session = _make_session(opgave=opgave)

    with app.test_request_context(
        "/api/ressource",
        method="POST",
        json={"name": "R", "url": "https://example.com", "OpgaveID": 2},
        headers={"usermail": "ansvarlig@example.com", "roles": "User"},
    ):
        with patch.object(ressource_controller.db_client, "get_session", return_value=session):
            resp, status = ressource_controller.create_ressource()

    assert status == 201
    assert resp.get_json()["message"] == "Ressource created successfully"


def test_create_ressource_template_denies_non_admin():
    app = Flask(__name__)

    skabelon = Opgaveskabelon()
    skabelon.OpgaveskabelonID = 5

    session = _make_session(opgaveskabelon=skabelon)

    with app.test_request_context(
        "/api/ressource",
        method="POST",
        json={"name": "R", "url": "https://example.com", "OpgaveskabelonID": 5},
        headers={"usermail": "ansvarlig@example.com", "roles": "User"},
    ):
        with patch.object(ressource_controller.db_client, "get_session", return_value=session):
            resp, status = ressource_controller.create_ressource()

    assert status == 403
    assert resp.get_json()["error"] == "Forbidden"

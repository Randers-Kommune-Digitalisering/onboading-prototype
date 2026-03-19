from io import BytesIO
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

    added = {}

    def add_side_effect(obj):
        if isinstance(obj, Ressource):
            added["ressource"] = obj

    def flush_side_effect():
        ressource = added.get("ressource")
        if ressource is not None and getattr(ressource, "RessourceID", None) is None:
            ressource.RessourceID = 123

    session.add.side_effect = add_side_effect
    session.flush.side_effect = flush_side_effect

    return session


def test_create_ressource_file_denies_when_not_admin_and_not_ansvarlig():
    app = Flask(__name__)

    opgave = Opgave()
    opgave.OpgaveID = 1
    opgave.ansvarligEmail = "ansvarlig@example.com"

    session = _make_session(opgave=opgave)

    payload = {
        "name": "R",
        "OpgaveID": "1",
        "file": (BytesIO(b"hello"), "a.txt"),
    }

    with app.test_request_context(
        "/api/ressource/file",
        method="POST",
        data=payload,
        content_type="multipart/form-data",
        headers={"usermail": "other@example.com", "roles": "User"},
    ):
        with patch.object(ressource_controller.db_client, "get_session", return_value=session):
            resp, status = ressource_controller.create_ressource_file()

    assert status == 403
    assert resp.get_json()["error"] == "Forbidden"


def test_create_ressource_file_allows_ansvarlig_case_insensitive_and_trimmed():
    app = Flask(__name__)

    opgave = Opgave()
    opgave.OpgaveID = 2
    opgave.ansvarligEmail = "  Ansvarlig@Example.com  "

    session = _make_session(opgave=opgave)

    payload = {
        "name": "R",
        "OpgaveID": "2",
        "file": (BytesIO(b"hello"), "a.txt"),
    }

    with app.test_request_context(
        "/api/ressource/file",
        method="POST",
        data=payload,
        content_type="multipart/form-data",
        headers={"usermail": "ansvarlig@example.com", "roles": "User"},
    ):
        with patch.object(ressource_controller.db_client, "get_session", return_value=session):
            resp, status = ressource_controller.create_ressource_file()

    assert status == 201
    body = resp.get_json()
    assert body["message"] == "Ressource created successfully"
    assert body["isFile"] is True
    assert body["RessourceID"] == 123


def test_create_ressource_file_template_denies_non_admin():
    app = Flask(__name__)

    skabelon = Opgaveskabelon()
    skabelon.OpgaveskabelonID = 5

    session = _make_session(opgaveskabelon=skabelon)

    payload = {
        "name": "R",
        "OpgaveskabelonID": "5",
        "file": (BytesIO(b"hello"), "a.txt"),
    }

    with app.test_request_context(
        "/api/ressource/file",
        method="POST",
        data=payload,
        content_type="multipart/form-data",
        headers={"usermail": "user@example.com", "roles": "User"},
    ):
        with patch.object(ressource_controller.db_client, "get_session", return_value=session):
            resp, status = ressource_controller.create_ressource_file()

    assert status == 403
    assert resp.get_json()["error"] == "Forbidden"


def test_create_ressource_file_rejects_invalid_file_type():
    app = Flask(__name__)

    opgave = Opgave()
    opgave.OpgaveID = 3
    opgave.ansvarligEmail = "ansvarlig@example.com"

    session = _make_session(opgave=opgave)

    payload = {
        "name": "R",
        "OpgaveID": "3",
        "file": (BytesIO(b"hello"), "somefile.exe"),
    }

    with app.test_request_context(
        "/api/ressource/file",
        method="POST",
        data=payload,
        content_type="multipart/form-data",
        headers={"usermail": "ansvarlig@example.com", "roles": "User"},
    ):
        with patch.object(ressource_controller.db_client, "get_session", return_value=session):
            resp, status = ressource_controller.create_ressource_file()

    assert status == 400
    assert resp.get_json()["error"] == "Unsupported file type"

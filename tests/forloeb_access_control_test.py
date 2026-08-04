from datetime import datetime
from unittest.mock import MagicMock, patch

from flask import Flask

from controllers import forloeb_controller, opgave_controller
from models import Forløb, Opgave, OpgaveGruppe


def _make_session(*, forloeb: Forløb, ansvarlig_exists: bool, opgaver: list[Opgave] | None = None):
    session = MagicMock()

    forloeb_query = MagicMock()
    forloeb_query.filter_by.return_value.first.return_value = forloeb

    opgave_query = MagicMock()
    opgave_query.filter.return_value.first.return_value = (Opgave() if ansvarlig_exists else None)
    opgave_query.options.return_value.filter_by.return_value.all.return_value = opgaver or []

    gruppe_query = MagicMock()
    gruppe_query.filter_by.return_value.all.return_value = []

    def query_side_effect(model):
        if model is Forløb:
            return forloeb_query
        if model is Opgave:
            return opgave_query
        if model is OpgaveGruppe:
            return gruppe_query
        return MagicMock()

    session.query.side_effect = query_side_effect
    return session


def test_get_forloeb_denies_unrelated_user():
    app = Flask(__name__)

    forloeb = Forløb()
    forloeb.ForløbID = 1
    forloeb.name = "Test"
    forloeb.usermail = "owner@example.com"
    forloeb.userdq = ""
    forloeb.admin = "admin@example.com"
    forloeb.startdate = None
    forloeb.enddate = None
    forloeb.isPreparation = False
    forloeb.varighed = 30
    forloeb.mails = []

    session = _make_session(forloeb=forloeb, ansvarlig_exists=False)

    with app.test_request_context(
        "/api/forloeb/1",
        method="GET",
        headers={"usermail": "other@example.com", "roles": "User"},
    ):
        with patch.object(forloeb_controller.db_client, "get_session", return_value=session):
            resp, status = forloeb_controller.get_forloeb(1)

    assert status == 403
    assert resp.get_json()["error"] == "Forbidden"


def test_get_forloeb_allows_owner_email_case_insensitive():
    app = Flask(__name__)

    forloeb = Forløb()
    forloeb.ForløbID = 2
    forloeb.name = "Test"
    forloeb.usermail = "Owner@Example.com"
    forloeb.userdq = ""
    forloeb.admin = "admin@example.com"
    forloeb.startdate = datetime(2026, 1, 1)
    forloeb.enddate = datetime(2026, 2, 1)
    forloeb.isPreparation = False
    forloeb.varighed = 30
    forloeb.mails = []

    session = _make_session(forloeb=forloeb, ansvarlig_exists=False)

    with app.test_request_context(
        "/api/forloeb/2",
        method="GET",
        headers={"usermail": "owner@example.com", "roles": "User"},
    ):
        with patch.object(forloeb_controller.db_client, "get_session", return_value=session):
            resp, status = forloeb_controller.get_forloeb(2)

    assert status == 200
    assert resp.get_json()["ForløbID"] == 2


def test_get_forloeb_allows_ansvarlig_on_any_task():
    app = Flask(__name__)

    forloeb = Forløb()
    forloeb.ForløbID = 3
    forloeb.name = "Test"
    forloeb.usermail = "owner@example.com"
    forloeb.userdq = ""
    forloeb.admin = "admin@example.com"
    forloeb.startdate = None
    forloeb.enddate = None
    forloeb.isPreparation = False
    forloeb.varighed = 30
    forloeb.mails = []

    session = _make_session(forloeb=forloeb, ansvarlig_exists=True)

    with app.test_request_context(
        "/api/forloeb/3",
        method="GET",
        headers={"usermail": "ansvarlig@example.com", "roles": "User"},
    ):
        with patch.object(forloeb_controller.db_client, "get_session", return_value=session):
            resp, status = forloeb_controller.get_forloeb(3)

    assert status == 200
    assert resp.get_json()["ForløbID"] == 3


def test_get_opgaver_forloeb_denies_unrelated_user():
    app = Flask(__name__)

    forloeb = Forløb()
    forloeb.ForløbID = 10
    forloeb.usermail = "owner@example.com"

    session = _make_session(forloeb=forloeb, ansvarlig_exists=False, opgaver=[])

    with app.test_request_context(
        "/api/opgave/forloeb/10",
        method="GET",
        headers={"usermail": "other@example.com", "roles": "User"},
    ):
        with patch.object(opgave_controller.db_client, "get_session", return_value=session):
            resp, status = opgave_controller.get_opgave_by_forloeb_id(10)

    assert status == 403
    assert resp.get_json()["error"] == "Forbidden"


def test_get_opgaver_forloeb_allows_ansvarlig_and_returns_tasks():
    app = Flask(__name__)

    forloeb = Forløb()
    forloeb.ForløbID = 11
    forloeb.usermail = "owner@example.com"

    task = Opgave()
    task.OpgaveID = 99
    task.title = "T"
    task.beskrivelse = "B"
    task.ansvarlig = "A"
    task.ansvarligEmail = "ansvarlig@example.com"
    task.startdato = None
    task.slutdato = None
    task.relativ_startdag = None
    task.relativ_slutdag = None
    task.result = False
    task.booking = None
    task.timestamp = datetime(2026, 3, 1)
    task.ressource = []
    task.opgavegruppe = None

    session = _make_session(forloeb=forloeb, ansvarlig_exists=True, opgaver=[task])

    with app.test_request_context(
        "/api/opgave/forloeb/11",
        method="GET",
        headers={"usermail": "ansvarlig@example.com", "roles": "User"},
    ):
        with patch.object(opgave_controller.db_client, "get_session", return_value=session):
            resp = opgave_controller.get_opgave_by_forloeb_id(11)

    # The controller returns jsonify(list) on success (no explicit status)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data[0]["OpgaveID"] == 99

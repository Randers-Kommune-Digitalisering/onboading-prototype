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


def test_get_opgaver_forloeb_hides_hidden_for_owner_user():
    app = Flask(__name__)

    forloeb = Forløb()
    forloeb.ForløbID = 12
    forloeb.usermail = "owner@example.com"

    visible_task = Opgave()
    visible_task.OpgaveID = 100
    visible_task.title = "Visible"
    visible_task.beskrivelse = "B"
    visible_task.ansvarlig = "A"
    visible_task.ansvarligEmail = "ansvarlig@example.com"
    visible_task.hidden = False
    visible_task.startdato = None
    visible_task.slutdato = None
    visible_task.relativ_startdag = None
    visible_task.relativ_slutdag = None
    visible_task.result = False
    visible_task.booking = None
    visible_task.timestamp = datetime(2026, 3, 1)
    visible_task.ressource = []
    visible_task.opgavegruppe = None

    hidden_task = Opgave()
    hidden_task.OpgaveID = 101
    hidden_task.title = "Hidden"
    hidden_task.beskrivelse = "B"
    hidden_task.ansvarlig = "A"
    hidden_task.ansvarligEmail = "ansvarlig@example.com"
    hidden_task.hidden = True
    hidden_task.startdato = None
    hidden_task.slutdato = None
    hidden_task.relativ_startdag = None
    hidden_task.relativ_slutdag = None
    hidden_task.result = False
    hidden_task.booking = None
    hidden_task.timestamp = datetime(2026, 3, 1)
    hidden_task.ressource = []
    hidden_task.opgavegruppe = None

    session = _make_session(forloeb=forloeb, ansvarlig_exists=False, opgaver=[visible_task, hidden_task])

    with app.test_request_context(
        "/api/opgave/forloeb/12",
        method="GET",
        headers={"usermail": "owner@example.com", "roles": "User"},
    ):
        with patch.object(opgave_controller.db_client, "get_session", return_value=session):
            resp = opgave_controller.get_opgave_by_forloeb_id(12)

    assert resp.status_code == 200
    data = resp.get_json()
    assert [task["OpgaveID"] for task in data] == [100]


def test_get_opgaver_forloeb_shows_hidden_for_matching_ansvarlig_only():
    app = Flask(__name__)

    forloeb = Forløb()
    forloeb.ForløbID = 13
    forloeb.usermail = "owner@example.com"

    visible_task = Opgave()
    visible_task.OpgaveID = 110
    visible_task.title = "Visible"
    visible_task.beskrivelse = "B"
    visible_task.ansvarlig = "A"
    visible_task.ansvarligEmail = "third@example.com"
    visible_task.hidden = False
    visible_task.startdato = None
    visible_task.slutdato = None
    visible_task.relativ_startdag = None
    visible_task.relativ_slutdag = None
    visible_task.result = False
    visible_task.booking = None
    visible_task.timestamp = datetime(2026, 3, 1)
    visible_task.ressource = []
    visible_task.opgavegruppe = None

    hidden_for_current = Opgave()
    hidden_for_current.OpgaveID = 111
    hidden_for_current.title = "Hidden Mine"
    hidden_for_current.beskrivelse = "B"
    hidden_for_current.ansvarlig = "A"
    hidden_for_current.ansvarligEmail = "ansvarlig@example.com"
    hidden_for_current.hidden = True
    hidden_for_current.startdato = None
    hidden_for_current.slutdato = None
    hidden_for_current.relativ_startdag = None
    hidden_for_current.relativ_slutdag = None
    hidden_for_current.result = False
    hidden_for_current.booking = None
    hidden_for_current.timestamp = datetime(2026, 3, 1)
    hidden_for_current.ressource = []
    hidden_for_current.opgavegruppe = None

    hidden_for_other = Opgave()
    hidden_for_other.OpgaveID = 112
    hidden_for_other.title = "Hidden Other"
    hidden_for_other.beskrivelse = "B"
    hidden_for_other.ansvarlig = "A"
    hidden_for_other.ansvarligEmail = "other@example.com"
    hidden_for_other.hidden = True
    hidden_for_other.startdato = None
    hidden_for_other.slutdato = None
    hidden_for_other.relativ_startdag = None
    hidden_for_other.relativ_slutdag = None
    hidden_for_other.result = False
    hidden_for_other.booking = None
    hidden_for_other.timestamp = datetime(2026, 3, 1)
    hidden_for_other.ressource = []
    hidden_for_other.opgavegruppe = None

    session = _make_session(
        forloeb=forloeb,
        ansvarlig_exists=True,
        opgaver=[visible_task, hidden_for_current, hidden_for_other],
    )

    with app.test_request_context(
        "/api/opgave/forloeb/13",
        method="GET",
        headers={"usermail": "ansvarlig@example.com", "roles": "User"},
    ):
        with patch.object(opgave_controller.db_client, "get_session", return_value=session):
            resp = opgave_controller.get_opgave_by_forloeb_id(13)

    assert resp.status_code == 200
    data = resp.get_json()
    assert [task["OpgaveID"] for task in data] == [110, 111]

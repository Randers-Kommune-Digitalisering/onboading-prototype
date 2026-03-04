import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from flask import jsonify, request

from models import Forløb, Opgave, OpgaveGruppe, Ressource
from utils.db_connection import get_db_client
from utils.mail_service import send_mail, create_mail_external_access

logger = logging.getLogger(__name__)

db_client = get_db_client()


def _utc_now():
    return datetime.now(timezone.utc)


def _hash_access_key(access_key: str) -> str:
    return hashlib.sha256(access_key.encode('utf-8')).hexdigest()


def _is_valid_access_key(forloeb: Forløb, access_key: str) -> bool:
    if not access_key or not isinstance(access_key, str):
        return False
    if not getattr(forloeb, 'external_access_key_hash', None):
        return False
    expires_at = getattr(forloeb, 'external_access_expires_at', None)
    if not expires_at:
        return False

    # DB timestamps may be naive; treat them as UTC.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if _utc_now() > expires_at:
        return False

    candidate_hash = _hash_access_key(access_key)
    return hmac.compare_digest(candidate_hash, forloeb.external_access_key_hash)


def request_external_access():
    """POST /api/external/request-access { forloebId: number }

    Always returns a generic success response to reduce enumeration.
    """
    payload = request.get_json(silent=True) or {}
    forloeb_id = payload.get('forloebId')

    try:
        forloeb_id_int = int(forloeb_id)
    except (TypeError, ValueError):
        # Generic response
        return jsonify({"message": "If the forløb exists, an email has been sent."}), 200

    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id_int).first()
        if not forloeb:
            return jsonify({"message": "If the forløb exists, an email has been sent."}), 200

        access_key = secrets.token_urlsafe(32)
        expires_at = _utc_now() + timedelta(hours=1)

        forloeb.external_access_key_hash = _hash_access_key(access_key)
        forloeb.external_access_expires_at = expires_at.replace(tzinfo=None)
        session.commit()

        base_url = request.url_root.rstrip('/')
        query = urlencode({"id": forloeb_id_int, "external": "true", "accessKey": access_key})
        link = f"{base_url}/forloeb-overview?{query}"

        subject, message = create_mail_external_access(forloeb, link, expires_at)
        sent = send_mail(forloeb.usermail, subject, message, attachments=None, reply_to=forloeb.admin)
        if not sent:
            logger.error("Failed sending external access email for ForløbID=%s with link %s", forloeb_id_int, link)

        return jsonify({"message": "If the forløb exists, an email has been sent."}), 200

    except Exception as e:
        session.rollback()
        logger.exception("Error requesting external access: %s", e)
        # Generic response
        return jsonify({"message": "If the forløb exists, an email has been sent."}), 200
    finally:
        session.close()


def get_external_userinfo():
    """GET /api/external/userinfo?forloebId=..&accessKey=..

    Returns a Public userInfo with the forløb usermail as email.
    """
    forloeb_id = request.args.get('forloebId')
    access_key = request.args.get('accessKey', '')

    try:
        forloeb_id_int = int(forloeb_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid access"}), 403

    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id_int).first()
        if not forloeb or not _is_valid_access_key(forloeb, access_key):
            return jsonify({"error": "Invalid access"}), 403

        return jsonify({
            "roles": ["Public"],
            "email": forloeb.usermail,
        }), 200
    finally:
        session.close()


def get_forloeb_external(forloeb_id: int):
    """GET /api/external/forloeb/<id>?accessKey=.. (read-only)."""
    access_key = request.args.get('accessKey', '')

    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id).first()
        if not forloeb or not _is_valid_access_key(forloeb, access_key):
            return jsonify({"error": "Invalid access"}), 403

        opgave_grupper = session.query(OpgaveGruppe).filter_by(ForløbID=forloeb.ForløbID).all()

        result = {
            "ForløbID": forloeb.ForløbID,
            "name": forloeb.name,
            "startdate": forloeb.startdate.isoformat() if forloeb.startdate else None,
            "enddate": forloeb.enddate.isoformat() if forloeb.enddate else None,
            "usermail": forloeb.usermail,
            "userdq": forloeb.userdq,
            "opgave_grupper": [
                {
                    "OpgaveGruppeID": gruppe.OpgaveGruppeID,
                    "name": gruppe.name,
                    "letter": gruppe.letter,
                }
                for gruppe in opgave_grupper
            ],
            "isPreparation": forloeb.isPreparation,
            "varighed": forloeb.varighed,
            "pending_emails": [],
        }

        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-store'
        return response, 200
    finally:
        session.close()


def get_opgaver_forloeb_external(forloeb_id: int):
    """GET /api/external/opgave/forloeb/<id>?accessKey=.. (read-only)."""
    access_key = request.args.get('accessKey', '')

    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id).first()
        if not forloeb or not _is_valid_access_key(forloeb, access_key):
            return jsonify({"error": "Invalid access"}), 403

        opgaver = session.query(Opgave).filter_by(ForløbID=forloeb_id).all()

        result = []
        for opgave in opgaver:
            ressources = session.query(Ressource).filter_by(OpgaveID=opgave.OpgaveID).all()
            result.append({
                "OpgaveID": opgave.OpgaveID,
                "title": opgave.title,
                "beskrivelse": opgave.beskrivelse,
                "ansvarlig": opgave.ansvarlig,
                "ansvarligEmail": opgave.ansvarligEmail,
                "startdato": opgave.startdato.isoformat() if opgave.startdato else None,
                "slutdato": opgave.slutdato.isoformat() if opgave.slutdato else None,
                "relativ_startdag": opgave.relativ_startdag,
                "relativ_slutdag": opgave.relativ_slutdag,
                "result": opgave.result,
                "booking": opgave.booking.isoformat() if opgave.booking else None,
                "timestamp": opgave.timestamp.isoformat() if opgave.timestamp else None,
                "ForløbID": opgave.ForløbID,
                "OpgaveGruppeID": opgave.OpgaveGruppeID,
                "note": opgave.note,
                "ressource": [
                    {
                        "RessourceID": r.RessourceID,
                        "name": r.name,
                        "url": r.url,
                        "OpgaveID": r.OpgaveID,
                    }
                    for r in ressources
                ],
            })

        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-store'
        return response, 200
    finally:
        session.close()

import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from flask import jsonify, request
from sqlalchemy.orm import selectinload

from models import Forløb, Opgave, OpgaveGruppe
from utils.db_connection import get_db_client
from controllers.mail_controller import send_mail, create_mail_external_access

logger = logging.getLogger(__name__)

db_client = get_db_client()


_EXTERNAL_ACCESS_TTL = timedelta(hours=1)
_EXTERNAL_ACCESS_COOLDOWN = timedelta(minutes=1)


def _utc_now():
    return datetime.now(timezone.utc)


def _hash_access_key(access_key: str) -> str:
    return hashlib.sha256(access_key.encode('utf-8')).hexdigest()


def _get_access_key_from_request(default: str = '') -> str:
    """Fetch accessKey without relying on URL query params.

    Uses header-based transport to avoid access keys being captured in URL logs.
    """
    header_value = request.headers.get('X-External-Access-Key')
    if header_value:
        return header_value
    return default


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

        # Basic throttling to reduce email spam: do not re-issue/send if an unexpired
        # key was generated very recently for this Forløb.
        existing_hash = getattr(forloeb, 'external_access_key_hash', None)
        existing_expires_at = getattr(forloeb, 'external_access_expires_at', None)
        if existing_hash and existing_expires_at:
            expires_at = existing_expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            now = _utc_now()

            if now < expires_at:
                issued_at = expires_at - _EXTERNAL_ACCESS_TTL
                if now - issued_at < _EXTERNAL_ACCESS_COOLDOWN:
                    return jsonify({"message": "If the forløb exists, an email has been sent."}), 200

        access_key = secrets.token_urlsafe(32)
        expires_at = _utc_now() + _EXTERNAL_ACCESS_TTL

        forloeb.external_access_key_hash = _hash_access_key(access_key)
        forloeb.external_access_expires_at = expires_at.replace(tzinfo=None)
        session.commit()

        base_url = request.url_root.rstrip('/')
        # Put accessKey in the URL fragment to avoid it being sent in Referer headers
        # and being captured in query-string logs. The SPA reads the fragment.
        query = urlencode({"id": forloeb_id_int, "external": "true"})
        link = f"{base_url}/forloeb-overview?{query}#accessKey={access_key}"

        subject, message = create_mail_external_access(forloeb, link, expires_at)
        sent = send_mail(forloeb.usermail, subject, message, attachments=None, reply_to=forloeb.admin)
        if not sent:
            logger.error("Failed sending external access email for ForløbID=%s", forloeb_id_int)

        return jsonify({"message": "If the forløb exists, an email has been sent."}), 200

    except Exception as e:
        session.rollback()
        logger.exception("Error requesting external access: %s", e)
        # Generic response
        return jsonify({"message": "If the forløb exists, an email has been sent."}), 200
    finally:
        session.close()


def get_external_userinfo():
    """GET /api/external/userinfo?forloebId=..

    The access key is expected in the `X-External-Access-Key` header.

    Returns a Public userInfo with the forløb usermail as email.
    """
    forloeb_id = request.args.get('forloebId')
    access_key = _get_access_key_from_request('')

    try:
        forloeb_id_int = int(forloeb_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid access"}), 403

    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id_int).first()
        if not forloeb or not _is_valid_access_key(forloeb, access_key):
            return jsonify({"error": "Invalid access"}), 403

        response = jsonify({
            "roles": ["Public"],
            "email": forloeb.usermail,
        })
        response.headers['Cache-Control'] = 'no-store'
        return response, 200
    finally:
        session.close()


def get_forloeb_external(forloeb_id: int):
    """GET /api/external/forloeb/<id> (read-only).

    The access key is expected in the `X-External-Access-Key` header.
    """
    access_key = _get_access_key_from_request('')

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
    """GET /api/external/opgave/forloeb/<id> (read-only).

    The access key is expected in the `X-External-Access-Key` header.
    """
    access_key = _get_access_key_from_request('')

    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id).first()
        if not forloeb or not _is_valid_access_key(forloeb, access_key):
            return jsonify({"error": "Invalid access"}), 403

        # Avoid N+1 queries when iterating opgaver and accessing relationships.
        opgaver = (
            session.query(Opgave)
            .options(
                selectinload(Opgave.ressource),
                selectinload(Opgave.opgavegruppe),
            )
            .filter_by(ForløbID=forloeb_id)
            .all()
        )

        result = []
        for opgave in opgaver:
            result.append({
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [
                    {
                        'RessourceID': ressource.RessourceID,
                        'name': ressource.name,
                        'url': ressource.url
                    } for ressource in opgave.ressource
                ],
                'gruppe': {
                    'OpgaveGruppeID': opgave.opgavegruppe.OpgaveGruppeID,
                    'name': opgave.opgavegruppe.name,
                    'letter': opgave.opgavegruppe.letter
                } if opgave.opgavegruppe else None,
                'ansvarlig': opgave.ansvarlig,
                'ansvarligEmail': opgave.ansvarligEmail,
                'startdato': opgave.startdato.isoformat() if opgave.startdato else None,
                'slutdato': opgave.slutdato.isoformat() if opgave.slutdato else None,
                'relativ_startdag': opgave.relativ_startdag,
                'relativ_slutdag': opgave.relativ_slutdag,
                'result': opgave.result,
                'booking': opgave.booking.isoformat() if opgave.booking else None,
                'timestamp': opgave.timestamp.isoformat()
            })

        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-store'
        return response, 200
    finally:
        session.close()

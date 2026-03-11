from __future__ import annotations

from io import BytesIO
from pathlib import Path

from flask import request, jsonify, send_file
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from models import Ressource, RessourceFile, Opgave, Opgaveskabelon
from utils.db_connection import get_db_client
from utils.access_control import (
    get_current_user_email,
    is_current_user_admin,
    user_can_access_forloeb,
)
from utils.ressource_serialization import serialize_ressource
from utils.config import MAX_UPLOAD_BYTES

db_client = get_db_client()


_ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
}


def _safe_filename(value: str) -> str:
    value = (value or "").strip()
    return value or "download"


def _is_allowed_filename(filename: str) -> bool:
    suffix = Path(filename or "").suffix.lower()
    return suffix in _ALLOWED_EXTENSIONS


def _download_response(file_row: RessourceFile):
    data = file_row.data or b""
    bio = BytesIO(data)
    bio.seek(0)
    resp = send_file(
        bio,
        mimetype=file_row.content_type or "application/octet-stream",
        as_attachment=True,
        download_name=_safe_filename(file_row.filename),
        max_age=0,
    )
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    return resp


def create_ressource():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['name', 'url']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        current_user_email = get_current_user_email()
        is_admin = is_current_user_admin()

        new_ressource = Ressource(
            name=data['name'],
            url=data['url'],
            isFile=False,
        )

        if 'OpgaveID' in data:
            opgave = session.query(Opgave).filter_by(OpgaveID=data['OpgaveID']).first()
            if not opgave:
                return jsonify({"error": "Opgave not found"}), 404

            if not is_admin:
                ansvarlig_email = (getattr(opgave, 'ansvarligEmail', None) or '').strip().lower()
                if not current_user_email or ansvarlig_email != current_user_email:
                    return jsonify({"error": "Forbidden"}), 403

            new_ressource.OpgaveID = opgave.OpgaveID
        elif 'OpgaveskabelonID' in data:
            if not is_admin:
                return jsonify({"error": "Forbidden"}), 403

            opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=data['OpgaveskabelonID']).first()
            if not opgaveskabelon:
                return jsonify({"error": "Opgaveskabelon not found"}), 404
            new_ressource.OpgaveskabelonID = opgaveskabelon.OpgaveskabelonID
        else:
            return jsonify({"error": "Either OpgaveID or OpgaveskabelonID is required"}), 400

        session.add(new_ressource)
        session.commit()
        return jsonify({"message": "Ressource created successfully"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def delete_ressource(ressource_id):
    session = db_client.get_session()
    try:
        ressource = session.query(Ressource).filter_by(RessourceID=ressource_id).first()
        if not ressource:
            return jsonify({"error": "Ressource not found"}), 404

        if not is_current_user_admin():
            current_user_email = get_current_user_email()
            if ressource.OpgaveskabelonID is not None:
                return jsonify({"error": "Forbidden"}), 403
            if ressource.OpgaveID is None:
                return jsonify({"error": "Forbidden"}), 403

            opgave = session.query(Opgave).filter_by(OpgaveID=ressource.OpgaveID).first()
            if not opgave:
                return jsonify({"error": "Opgave not found"}), 404

            ansvarlig_email = (getattr(opgave, 'ansvarligEmail', None) or '').strip().lower()
            if not current_user_email or ansvarlig_email != current_user_email:
                return jsonify({"error": "Forbidden"}), 403

        session.delete(ressource)
        session.commit()
        return jsonify({"message": "Ressource deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_ressource(ressource_id):
    session = db_client.get_session()
    try:
        ressource = session.query(Ressource).filter_by(RessourceID=ressource_id).first()
        if not ressource:
            return jsonify({"error": "Ressource not found"}), 404

        if not is_current_user_admin():
            current_user_email = get_current_user_email()
            if ressource.OpgaveskabelonID is not None:
                return jsonify({"error": "Forbidden"}), 403
            if ressource.OpgaveID is None:
                return jsonify({"error": "Forbidden"}), 403

            opgave = session.query(Opgave).filter_by(OpgaveID=ressource.OpgaveID).first()
            if not opgave:
                return jsonify({"error": "Opgave not found"}), 404

            ansvarlig_email = (getattr(opgave, 'ansvarligEmail', None) or '').strip().lower()
            if not current_user_email or ansvarlig_email != current_user_email:
                return jsonify({"error": "Forbidden"}), 403

        data = request.json
        ressource.name = data.get('name', ressource.name)
        # Do not allow updating the url for file-backed resources.
        if not getattr(ressource, 'isFile', False):
            ressource.url = data.get('url', ressource.url)

        session.commit()
        return jsonify({"message": "Ressource updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_ressource(ressource_id):
    session = db_client.get_session()
    try:
        ressource = (
            session.query(Ressource)
            .options(selectinload(Ressource.file).defer(RessourceFile.data))
            .filter_by(RessourceID=ressource_id)
            .first()
        )
        if not ressource:
            return jsonify({"error": "Ressource not found"}), 404

        result = serialize_ressource(ressource)
        result.update({
            "OpgaveID": ressource.OpgaveID,
            "OpgaveskabelonID": ressource.OpgaveskabelonID,
        })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_ressources_by_opgaveid(opgave_id):
    session = db_client.get_session()
    try:
        ressources = (
            session.query(Ressource)
            .options(selectinload(Ressource.file).defer(RessourceFile.data))
            .filter_by(OpgaveID=opgave_id)
            .all()
        )
        if not ressources:
            return jsonify([])

        return jsonify([serialize_ressource(ressource) for ressource in ressources])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_ressources_by_opgaveskabelonid(opgaveskabelon_id):
    session = db_client.get_session()
    try:
        ressources = (
            session.query(Ressource)
            .options(selectinload(Ressource.file).defer(RessourceFile.data))
            .filter_by(OpgaveskabelonID=opgaveskabelon_id)
            .all()
        )
        if not ressources:
            return jsonify([])

        return jsonify([serialize_ressource(ressource) for ressource in ressources])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def create_ressource_file():
    session = db_client.get_session()
    try:
        if request.content_length and request.content_length > MAX_UPLOAD_BYTES:
            return jsonify({"error": "File too large"}), 413

        name = (request.form.get('name') or '').strip()
        file = request.files.get('file')
        opgave_id_raw = request.form.get('OpgaveID')
        opgaveskabelon_id_raw = request.form.get('OpgaveskabelonID')

        if not name or not file:
            return jsonify({"error": "Missing required fields"}), 400

        filename = (file.filename or '').strip()
        if not filename or not _is_allowed_filename(filename):
            return jsonify({"error": "Unsupported file type"}), 400

        raw = file.read() or b''
        if len(raw) > MAX_UPLOAD_BYTES:
            return jsonify({"error": "File too large"}), 413

        current_user_email = get_current_user_email()
        is_admin = is_current_user_admin()

        new_ressource = Ressource(name=name, url='', isFile=True)

        if opgave_id_raw:
            try:
                opgave_id = int(opgave_id_raw)
            except (TypeError, ValueError):
                return jsonify({"error": "Invalid OpgaveID"}), 400

            opgave = session.query(Opgave).filter_by(OpgaveID=opgave_id).first()
            if not opgave:
                return jsonify({"error": "Opgave not found"}), 404

            if not is_admin:
                ansvarlig_email = (getattr(opgave, 'ansvarligEmail', None) or '').strip().lower()
                if not current_user_email or ansvarlig_email != current_user_email:
                    return jsonify({"error": "Forbidden"}), 403

            new_ressource.OpgaveID = opgave.OpgaveID

        elif opgaveskabelon_id_raw:
            if not is_admin:
                return jsonify({"error": "Forbidden"}), 403

            try:
                opgaveskabelon_id = int(opgaveskabelon_id_raw)
            except (TypeError, ValueError):
                return jsonify({"error": "Invalid OpgaveskabelonID"}), 400

            opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=opgaveskabelon_id).first()
            if not opgaveskabelon:
                return jsonify({"error": "Opgaveskabelon not found"}), 404

            new_ressource.OpgaveskabelonID = opgaveskabelon.OpgaveskabelonID
        else:
            return jsonify({"error": "Either OpgaveID or OpgaveskabelonID is required"}), 400

        session.add(new_ressource)
        session.flush()  # assign RessourceID

        new_ressource.url = f"/api/ressource/{new_ressource.RessourceID}/download"
        new_ressource.file = RessourceFile(
            RessourceID=new_ressource.RessourceID,
            filename=filename,
            content_type=getattr(file, 'mimetype', None),
            size_bytes=len(raw),
            data=raw,
        )

        session.commit()
        return jsonify({
            "message": "Ressource created successfully",
            "RessourceID": new_ressource.RessourceID,
            "name": new_ressource.name,
            "isFile": True,
            "filename": filename,
            "content_type": getattr(file, 'mimetype', None),
            "size_bytes": len(raw),
        }), 201

    except RequestEntityTooLarge:
        session.rollback()
        return jsonify({"error": "File too large"}), 413
    except HTTPException:
        # Let Flask handle HTTP errors (including app-level error handlers).
        raise
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def download_ressource_file(ressource_id: int):
    session = db_client.get_session()
    try:
        ressource = session.query(Ressource).filter_by(RessourceID=ressource_id).first()
        if not ressource:
            return jsonify({"error": "Ressource not found"}), 404

        if not getattr(ressource, 'isFile', False):
            return jsonify({"error": "Ressource is not a file"}), 404

        if not is_current_user_admin():
            current_user_email = get_current_user_email()

            # Templates: admin-only.
            if ressource.OpgaveskabelonID is not None:
                return jsonify({"error": "Forbidden"}), 403

            if ressource.OpgaveID is None:
                return jsonify({"error": "Forbidden"}), 403

            opgave = session.query(Opgave).filter_by(OpgaveID=ressource.OpgaveID).first()
            if not opgave:
                return jsonify({"error": "Opgave not found"}), 404

            forloeb_id = getattr(opgave, 'ForløbID', None)
            if forloeb_id is not None:
                if not user_can_access_forloeb(session, forloeb_id, current_user_email):
                    return jsonify({"error": "Forbidden"}), 403
            else:
                # Defensive fallback: allow only ansvarlig for opgaven.
                ansvarlig_email = (getattr(opgave, 'ansvarligEmail', None) or '').strip().lower()
                if not current_user_email or ansvarlig_email != current_user_email:
                    return jsonify({"error": "Forbidden"}), 403

        file_row = session.query(RessourceFile).filter_by(RessourceID=ressource.RessourceID).first()
        if not file_row:
            return jsonify({"error": "File not found"}), 404

        return _download_response(file_row)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

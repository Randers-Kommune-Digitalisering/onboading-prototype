from flask import request, jsonify
from datetime import datetime
from models import Opgave, Forløb, Forløbsskabelon, Opgaveskabelon, Ressource, RessourceFile, OpgaveGruppe
from utils.db_connection import get_db_client
from utils.config import MAIL_DESC_NEW_TASK_USER, MAIL_DESC_NEW_TASK_ANSVARLIG
from utils.access_control import get_current_user_email, is_current_user_admin, user_can_access_forloeb
from controllers.mail_controller import (
    plan_mail,
    create_mail_ansvarlig,
    create_mail_new_task_user
)
import logging
from sqlalchemy.orm import selectinload

db_client = get_db_client()
logger = logging.getLogger(__name__)


def _serialize_ressource(ressource: Ressource) -> dict:
    item = {
        'RessourceID': ressource.RessourceID,
        'name': ressource.name,
        'url': ressource.url,
        'isFile': bool(getattr(ressource, 'isFile', False)),
    }

    if item['isFile'] and getattr(ressource, 'file', None) is not None:
        item.update({
            'filename': ressource.file.filename,
            'content_type': ressource.file.content_type,
            'size_bytes': ressource.file.size_bytes,
        })

    return item


def create_opgave():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['title', 'beskrivelse', 'ansvarlig', 'ansvarligEmail', 'result', 'timestamp']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_opgave = Opgave(
            title=data['title'],
            beskrivelse=data['beskrivelse'],
            note=data['note'],
            ansvarlig=data['ansvarlig'],
            ansvarligEmail=data['ansvarligEmail'],
            startdato=datetime.fromisoformat(data['startdato']) if 'startdato' in data else None,
            slutdato=datetime.fromisoformat(data['slutdato']) if 'slutdato' in data else None,
            relativ_startdag=data['relativ_startdag'] if 'relativ_startdag' in data else None,
            relativ_slutdag=data['relativ_slutdag'] if 'relativ_slutdag' in data else None,
            result=data['result'],
            booking=datetime.fromisoformat(data['booking']) if 'booking' in data else None,
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        )

        if 'ForløbID' in data:
            forløb = session.query(Forløb).filter_by(ForløbID=data['ForløbID']).first()
            if not forløb:
                return jsonify({"error": "Forløb not found"}), 404
            new_opgave.forløb = forløb
        elif 'ForløbsskabelonID' in data:
            forløbsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=data['ForløbsskabelonID']).first()
            if not forløbsskabelon:
                return jsonify({"error": "Forløbsskabelon not found"}), 404
            new_opgave.forløbsskabelon = forløbsskabelon

            print(f"relativ_startdag: {new_opgave.relativ_startdag}, relativ_slutdag: {new_opgave.relativ_slutdag}")
            if 'relativ_startdag' not in data or 'relativ_slutdag' not in data:
                return jsonify({"error": "relativ_startdag and relativ_slutdag are required to create new opgaveskabelon"}), 400
        else:
            return jsonify({"error": "Either ForløbID or ForløbsskabelonID is required"}), 400

        if 'OpgaveGruppeID' in data:
            if data.get('OpgaveGruppeID') is None:
                new_opgave.opgavegruppe = None
            else:
                opgavegruppe = session.query(OpgaveGruppe).filter_by(OpgaveGruppeID=data['OpgaveGruppeID']).first()
                if not opgavegruppe:
                    return jsonify({"error": "OpgaveGruppe not found"}), 404
                new_opgave.opgavegruppe = opgavegruppe
        elif 'OpgaveGruppeNavn' in data:
            new_opgave.opgavegruppe = create_opgavegruppe(
                data['OpgaveGruppeNavn'],
                new_opgave.forløb.ForløbID if new_opgave.forløb is not None else None,
                new_opgave.forløbsskabelon.ForløbsskabelonID if new_opgave.forløbsskabelon is not None else None
            )

        session.add(new_opgave)
        session.commit()

        # Send mail notifications to the user and responsible person (ansvarlig)
        if new_opgave.startdato and new_opgave.slutdato:
            if new_opgave.ansvarligEmail and new_opgave.ansvarligEmail != "":
                subject, message = create_mail_ansvarlig(new_opgave)
                planned_mail = plan_mail(
                    new_opgave.ansvarligEmail,
                    subject,
                    message,
                    opgave_id=new_opgave.OpgaveID,
                    forloeb_id=new_opgave.ForløbID,
                    description=MAIL_DESC_NEW_TASK_ANSVARLIG,
                )
                if not planned_mail:
                    logger.error("Failed to plan email to ansvarlig")
            # Plan mail to the forløb user only when forløbet is started.
            forloeb = getattr(new_opgave, 'forløb', None)
            if forloeb is not None and getattr(forloeb, 'isPreparation', True) is False:
                if getattr(forloeb, 'usermail', None):
                    user_subject, user_message = create_mail_new_task_user(forloeb, new_opgave)
                    planned_user_mail = plan_mail(
                        forloeb.usermail,
                        user_subject,
                        user_message,
                        opgave_id=new_opgave.OpgaveID,
                        forloeb_id=forloeb.ForløbID,
                        description=MAIL_DESC_NEW_TASK_USER,
                    )
                    if not planned_user_mail:
                        logger.error("Failed to plan email to user")

        return jsonify({"message": "Opgave created successfully", "OpgaveID": new_opgave.OpgaveID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def create_opgavegruppe(name, forløb_id=None, forloeb_skabelon_id=None):
    if not forløb_id and not forloeb_skabelon_id:
        raise ValueError("ForløbID or ForløbsskabelonID is required to create OpgaveGruppe")
    session = db_client.get_session()
    try:
        new_opgavegruppe = OpgaveGruppe(name=name, letter=name[0].upper(), ForløbID=forløb_id, ForløbsskabelonID=forloeb_skabelon_id)
        session.add(new_opgavegruppe)
        session.commit()
        return new_opgavegruppe
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_opgaver():
    session = db_client.get_session()
    try:
        opgaver = (
            session.query(Opgave)
            .options(
                selectinload(Opgave.ressource),
                selectinload(Opgave.opgavegruppe),
            )
            .all()
        )
        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [_serialize_ressource(ressource) for ressource in opgave.ressource],
                'gruppe': {
                    'OpgaveGruppeID': opgave.opgavegruppe.OpgaveGruppeID,
                    'letter': opgave.opgavegruppe.letter,
                    'name': opgave.opgavegruppe.name
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
            } for opgave in opgaver
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def create_opgave_with_opgaveskabelon():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['OpgaveskabelonID']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=data['OpgaveskabelonID']).first()
        if not opgaveskabelon:
            return jsonify({"error": "Opgaveskabelon not found"}), 404

        new_opgave = Opgave(
            title=data.get('title', opgaveskabelon.title),
            beskrivelse=data.get('beskrivelse', opgaveskabelon.beskrivelse),
            note=data.get('note', opgaveskabelon.note),
            ansvarlig=data.get('ansvarlig', ""),
            ansvarligEmail=data.get('ansvarligEmail', ""),
            startdato=datetime.fromisoformat(data['startdato']) if 'startdato' in data else None,
            slutdato=datetime.fromisoformat(data['slutdato']) if 'slutdato' in data else None,
            relativ_startdag=data['relativ_startdag'] if 'relativ_startdag' in data else None,
            relativ_slutdag=data['relativ_slutdag'] if 'relativ_slutdag' in data else None,
            result=data.get('result', False),
            timestamp=datetime.now()
        )

        if 'ForløbID' in data:
            forløb = session.query(Forløb).filter_by(ForløbID=data['ForløbID']).first()
            if not forløb:
                return jsonify({"error": "Forløb not found"}), 404
            new_opgave.forløb = forløb
        elif 'ForløbsskabelonID' in data:
            forløbsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=data['ForløbsskabelonID']).first()
            if not forløbsskabelon:
                return jsonify({"error": "Forløbsskabelon not found"}), 404
            new_opgave.forløbsskabelon = forløbsskabelon
        else:
            return jsonify({"error": "Either ForløbID or ForløbsskabelonID is required"}), 400

        if 'OpgaveGruppeID' in data and data.get('OpgaveGruppeID') is not None:
            opgavegruppe = session.query(OpgaveGruppe).filter_by(OpgaveGruppeID=data['OpgaveGruppeID']).first()
            if not opgavegruppe:
                return jsonify({"error": "OpgaveGruppe not found"}), 404
            new_opgave.opgavegruppe = opgavegruppe
        elif 'OpgaveGruppeNavn' in data:
            new_opgave.opgavegruppe = create_opgavegruppe(
                data['OpgaveGruppeNavn'],
                new_opgave.forløb.ForløbID if new_opgave.forløb is not None else None,
                new_opgave.forløbsskabelon.ForløbsskabelonID if new_opgave.forløbsskabelon is not None else None
            )

        session.add(new_opgave)
        session.commit()

        for ressource in opgaveskabelon.ressource:
            if bool(getattr(ressource, 'isFile', False)):
                src_file = getattr(ressource, 'file', None)
                if src_file is None:
                    src_file = session.query(RessourceFile).filter_by(RessourceID=ressource.RessourceID).first()
                if src_file is None:
                    continue

                new_ressource = Ressource(
                    name=ressource.name,
                    url='',
                    isFile=True,
                    OpgaveID=new_opgave.OpgaveID,
                )
                session.add(new_ressource)
                session.flush()

                new_ressource.url = f"/api/ressource/{new_ressource.RessourceID}/download"
                new_ressource.file = RessourceFile(
                    RessourceID=new_ressource.RessourceID,
                    filename=src_file.filename,
                    content_type=src_file.content_type,
                    size_bytes=src_file.size_bytes,
                    data=src_file.data,
                )
            else:
                new_ressource = Ressource(
                    name=ressource.name,
                    url=ressource.url,
                    isFile=False,
                    OpgaveID=new_opgave.OpgaveID,
                )
                session.add(new_ressource)
        session.commit()

        # Send mail notifications to the user and responsible person (ansvarlig)
        if new_opgave.startdato and new_opgave.slutdato:
            if new_opgave.ansvarligEmail and new_opgave.ansvarligEmail != "":
                subject, message = create_mail_ansvarlig(new_opgave)
                planned_mail = plan_mail(
                    new_opgave.ansvarligEmail,
                    subject,
                    message,
                    opgave_id=new_opgave.OpgaveID,
                    forloeb_id=new_opgave.ForløbID,
                    description=MAIL_DESC_NEW_TASK_ANSVARLIG,
                )
                if not planned_mail:
                    logger.error("Failed to plan email to ansvarlig")

            forloeb = getattr(new_opgave, 'forløb', None)
            if forloeb is not None and getattr(forloeb, 'isPreparation', True) is False:
                if getattr(forloeb, 'usermail', None):
                    user_subject, user_message = create_mail_new_task_user(forloeb, new_opgave)
                    planned_user_mail = plan_mail(
                        forloeb.usermail,
                        user_subject,
                        user_message,
                        opgave_id=new_opgave.OpgaveID,
                        forloeb_id=forloeb.ForløbID,
                        description=MAIL_DESC_NEW_TASK_USER,
                    )
                    if not planned_user_mail:
                        logger.error("Failed to plan email to user")

        return jsonify({"message": "Opgave created successfully with Opgaveskabelon", "OpgaveID": new_opgave.OpgaveID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloebsskabelon_id(forlobsskabelon_id):
    session = db_client.get_session()
    try:
        usermail = request.headers.get('usermail')

        query = (
            session.query(Opgave)
            .options(
                selectinload(Opgave.ressource),
                selectinload(Opgave.opgavegruppe),
            )
            .join(Forløb)
            .filter(Opgave.ForløbsskabelonID == forlobsskabelon_id)
        )
        if usermail:
            query = query.filter(Forløb.usermail == usermail)

        opgave = query.all()

        if not opgave:
            return jsonify([])

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [_serialize_ressource(ressource) for ressource in opgave.ressource],
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
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave(opgave_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgave).filter_by(OpgaveID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgave not found"}), 404

        opgave_data = {
            'OpgaveID': opgave.OpgaveID,
            'title': opgave.title,
            'beskrivelse': opgave.beskrivelse,
            'note': opgave.note,
            'resourcer': [_serialize_ressource(ressource) for ressource in opgave.ressource],
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
            'timestamp': opgave.timestamp.isoformat(),
            'ForløbID': opgave.ForløbID,
            'ForløbsskabelonID': opgave.ForløbsskabelonID
        }
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloebsskabelon_id_admin(forlobsskabelon_id):
    session = db_client.get_session()
    try:
        opgave = (
            session.query(Opgave)
            .options(
                selectinload(Opgave.ressource),
                selectinload(Opgave.opgavegruppe),
            )
            .filter_by(ForløbsskabelonID=forlobsskabelon_id)
            .all()
        )
        if not opgave:
            return jsonify([])

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'note': opgave.note,
                'resourcer': [_serialize_ressource(ressource) for ressource in opgave.ressource],
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
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloeb_id_admin(forlob_id):
    session = db_client.get_session()
    try:
        opgave = (
            session.query(Opgave)
            .options(
                selectinload(Opgave.ressource),
                selectinload(Opgave.opgavegruppe),
                selectinload(Opgave.mails),
            )
            .filter_by(ForløbID=forlob_id)
            .all()
        )
        if not opgave:
            return jsonify([])

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'note': opgave.note,
                'resourcer': [_serialize_ressource(ressource) for ressource in opgave.ressource],
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
                'timestamp': opgave.timestamp.isoformat(),
                'pending_emails': [
                    {
                        'id': mail.MailID,
                        'recipient': mail.recipient,
                        'subject': mail.subject,
                        'description': mail.description
                    } for mail in opgave.mails if not mail.isSent
                ]
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_ansvarlig(usermail):
    session = db_client.get_session()
    try:
        usermail = get_current_user_email() or usermail
        if not usermail:
            return jsonify([])

        query = (
            session.query(Opgave)
            .options(
                selectinload(Opgave.ressource),
                selectinload(Opgave.opgavegruppe),
                selectinload(Opgave.forløb),
            )
            .filter(Opgave.ansvarligEmail.ilike(usermail.lower()))
        )
        opgave = query.all()

        if not opgave:
            return jsonify([])

        opgave_data = []
        for opg in opgave:
            forloeb_name = opg.forløb.name if getattr(opg, 'forløb', None) else None

            opgave_data.append({
                'OpgaveID': opg.OpgaveID,
                'ForløbID': opg.ForløbID,
                'ForløbsskabelonID': opg.ForløbsskabelonID,
                'name': forloeb_name,
                'title': opg.title,
                'beskrivelse': opg.beskrivelse,
                'note': opg.note,
                'resourcer': [_serialize_ressource(ressource) for ressource in opg.ressource],
                'gruppe': {
                    'OpgaveGruppeID': opg.opgavegruppe.OpgaveGruppeID,
                    'name': opg.opgavegruppe.name,
                    'letter': opg.opgavegruppe.letter
                } if opg.opgavegruppe else None,
                'ansvarlig': opg.ansvarlig,
                'ansvarligEmail': opg.ansvarligEmail,
                'startdato': opg.startdato.isoformat() if opg.startdato else None,
                'slutdato': opg.slutdato.isoformat() if opg.slutdato else None,
                'relativ_startdag': opg.relativ_startdag,
                'relativ_slutdag': opg.relativ_slutdag,
                'result': opg.result,
                'booking': opg.booking.isoformat() if opg.booking else None,
                'timestamp': opg.timestamp.isoformat()
            })

        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloeb_id(forlob_id):
    session = db_client.get_session()
    try:
        if not is_current_user_admin():
            user_email = get_current_user_email()
            if not user_can_access_forloeb(session, forlob_id, user_email):
                return jsonify({"error": "Forbidden"}), 403

        opgave = (
            session.query(Opgave)
            .options(
                selectinload(Opgave.ressource),
                selectinload(Opgave.opgavegruppe),
            )
            .filter_by(ForløbID=forlob_id)
            .all()
        )

        if not opgave:
            return jsonify([])

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [_serialize_ressource(ressource) for ressource in opgave.ressource],
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
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_opgave(opgave_id):
    session = db_client.get_session()
    try:
        data = request.json

        opgave = session.query(Opgave).filter_by(OpgaveID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgave not found"}), 404

        previous_opgavegruppe = opgave.opgavegruppe
        is_new_ansvarlig = opgave.ansvarlig != data.get('ansvarlig', opgave.ansvarlig)

        opgave.title = data.get('title', opgave.title)
        opgave.beskrivelse = data.get('beskrivelse', opgave.beskrivelse)
        opgave.note = data.get('note', opgave.note)
        if 'OpgaveGruppeID' in data:
            if data.get('OpgaveGruppeID') is None:
                opgave.opgavegruppe = None
            else:
                opgavegruppe = session.query(OpgaveGruppe).filter_by(OpgaveGruppeID=data['OpgaveGruppeID']).first()
                if not opgavegruppe:
                    return jsonify({"error": "OpgaveGruppe not found"}), 404
                opgave.opgavegruppe = opgavegruppe
        elif 'OpgaveGruppeNavn' in data:
            opgave.opgavegruppe = create_opgavegruppe(data['OpgaveGruppeNavn'], opgave.ForløbID or None, opgave.ForløbsskabelonID or None)
        if is_new_ansvarlig:
            opgave.ansvarlig = data.get('ansvarlig', opgave.ansvarlig)
            opgave.ansvarligEmail = data.get('ansvarligEmail', opgave.ansvarligEmail)
        opgave.startdato = datetime.fromisoformat(data['startdato']) if 'startdato' in data else opgave.startdato
        opgave.slutdato = datetime.fromisoformat(data['slutdato']) if 'slutdato' in data else opgave.slutdato
        opgave.relativ_startdag = data.get('relativ_startdag', opgave.relativ_startdag)
        opgave.relativ_slutdag = data.get('relativ_slutdag', opgave.relativ_slutdag)
        opgave.result = data.get('result', opgave.result)
        opgave.booking = datetime.fromisoformat(data['booking']) if 'booking' in data else opgave.booking,
        opgave.timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')) if 'timestamp' in data else opgave.timestamp

        session.commit()

        if previous_opgavegruppe and (opgave.opgavegruppe is None or previous_opgavegruppe.OpgaveGruppeID != opgave.opgavegruppe.OpgaveGruppeID):
            # Delete opgaveGruppe if no other tasks are part of it
            if not session.query(Opgave).filter_by(OpgaveGruppeID=previous_opgavegruppe.OpgaveGruppeID).first():
                if session.query(OpgaveGruppe).filter_by(OpgaveGruppeID=previous_opgavegruppe.OpgaveGruppeID).first():
                    session.delete(previous_opgavegruppe)
                    session.commit()

        # Send mail notification to the responsible person
        if opgave.startdato and opgave.slutdato and is_new_ansvarlig and opgave.ansvarligEmail is not None and opgave.ansvarligEmail != "":
            subject, message = create_mail_ansvarlig(opgave)
            planned_mail = plan_mail(opgave.ansvarligEmail, subject, message, opgave_id=opgave.OpgaveID, forloeb_id=opgave.ForløbID, description=MAIL_DESC_NEW_TASK_ANSVARLIG)
            if not planned_mail:
                logger.error("Failed to plan email")

        return jsonify({"message": "Opgave updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def delete_opgave(opgave_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgave).filter_by(OpgaveID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgave not found"}), 404

        gruppe = session.query(OpgaveGruppe).filter_by(OpgaveGruppeID=opgave.OpgaveGruppeID).first()

        session.delete(opgave)
        session.commit()

        if gruppe and not session.query(Opgave).filter_by(OpgaveGruppeID=gruppe.OpgaveGruppeID).first():
            session.delete(gruppe)
            session.commit()

        return jsonify({"message": "Opgave deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

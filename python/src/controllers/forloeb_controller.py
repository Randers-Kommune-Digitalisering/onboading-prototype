from flask import request, jsonify
from datetime import datetime, timedelta
from models import Forløb, Forløbsskabelon, Opgave, Ressource, OpgaveGruppe
from utils.db_connection import get_db_client
from utils.mail_service import plan_mail, create_mail_ansvarlig, create_mail_forloeb_start
import logging
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

db_client = get_db_client()


def create_forloeb():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['name', 'startdate', 'enddate', 'admin', 'usermail', 'userdq']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        forloeb = Forløb(
            name=data['name'],
            startdate=datetime.fromisoformat(data['startdate']),
            enddate=datetime.fromisoformat(data['enddate']),
            admin=data['admin'],
            usermail=data['usermail'],
            userdq=data['userdq'],
            isPreparation=False
        )
        session.add(forloeb)
        session.commit()

        if 'ForløbsskabelonID' in data:
            forløbsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=data['ForløbsskabelonID']).first()
            if not forløbsskabelon:
                return jsonify({"error": "Forløbsskabelon not found"}), 404

            skabelon_opgave_grupper = session.query(OpgaveGruppe).filter_by(ForløbsskabelonID=forløbsskabelon.ForløbsskabelonID).all()
            new_opgave_grupper = []
            for opgave_gruppe in skabelon_opgave_grupper:
                new_opgave_gruppe = OpgaveGruppe(
                    name=opgave_gruppe.name,
                    letter=opgave_gruppe.letter,
                    ForløbID=forloeb.ForløbID
                )
                session.add(new_opgave_gruppe)
                session.commit()  # Commit to get the new OpgaveGruppeID
                new_opgave_grupper.append(new_opgave_gruppe)

            for opgave in forløbsskabelon.opgave:
                # Find the matching OpgaveGruppe by name
                matching_gruppe = next((g for g in new_opgave_grupper if opgave.opgavegruppe and g.name == opgave.opgavegruppe.name), None)
                new_opgave = Opgave(
                    title=opgave.title,
                    beskrivelse=opgave.beskrivelse,
                    ansvarlig=opgave.ansvarlig,
                    ansvarligEmail=opgave.ansvarligEmail,
                    startdato=forloeb.startdate + timedelta(days=opgave.relativ_startdag),  # Adding relative days
                    slutdato=forloeb.startdate + timedelta(days=opgave.relativ_startdag) + timedelta(days=opgave.relativ_slutdag),
                    result=opgave.result,
                    timestamp=opgave.timestamp,
                    ForløbID=forloeb.ForløbID,
                    OpgaveGruppeID=matching_gruppe.OpgaveGruppeID if matching_gruppe else None
                )
                session.add(new_opgave)
                session.commit()  # Commit to get the new OpgaveID

                ressources = session.query(Ressource).filter_by(OpgaveID=opgave.OpgaveID).all()
                for ressource in ressources:
                    new_ressource = Ressource(
                        name=ressource.name,
                        url=ressource.url,
                        OpgaveID=new_opgave.OpgaveID  # Use the new OpgaveID
                    )
                    session.add(new_ressource)
                session.commit()

        return jsonify({"message": "Forløb created successfully", "uid": forloeb.ForløbID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def create_forloeb_preparation():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['name', 'admin', 'usermail', 'userdq']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        forløbsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=data['ForløbsskabelonID']).first() if 'ForløbsskabelonID' in data else None
        forloeb = Forløb(
            name=data['name'],
            varighed=forløbsskabelon.varighed if forløbsskabelon and forløbsskabelon.varighed else 30,
            startdate=None,  # Set when started
            enddate=None,    # Set when started
            admin=data['admin'],
            usermail=data['usermail'],
            userdq=data['userdq'],
            isPreparation=True
        )
        session.add(forloeb)
        session.commit()

        if not forløbsskabelon:
            return jsonify({"message": "Forløb preparation created successfully without template", "uid": forloeb.ForløbID}), 201

        skabelon_opgave_grupper = session.query(OpgaveGruppe).filter_by(ForløbsskabelonID=forløbsskabelon.ForløbsskabelonID).all()
        new_opgave_grupper = []
        for opgave_gruppe in skabelon_opgave_grupper:
            new_opgave_gruppe = OpgaveGruppe(
                name=opgave_gruppe.name,
                letter=opgave_gruppe.letter,
                ForløbID=forloeb.ForløbID
            )
            session.add(new_opgave_gruppe)
            session.commit()  # Commit to get the new OpgaveGruppeID
            new_opgave_grupper.append(new_opgave_gruppe)

        for opgave in forløbsskabelon.opgave:
            # Find the matching OpgaveGruppe by name
            matching_gruppe = next((g for g in new_opgave_grupper if opgave.opgavegruppe and g.name == opgave.opgavegruppe.name), None)
            new_opgave = Opgave(
                title=opgave.title,
                beskrivelse=opgave.beskrivelse,
                ansvarlig=opgave.ansvarlig,
                ansvarligEmail=opgave.ansvarligEmail,
                relativ_startdag=opgave.relativ_startdag,
                relativ_slutdag=opgave.relativ_slutdag,
                result=opgave.result,
                timestamp=opgave.timestamp,
                ForløbID=forloeb.ForløbID,
                OpgaveGruppeID=matching_gruppe.OpgaveGruppeID if matching_gruppe else None
            )
            session.add(new_opgave)
            session.commit()  # Commit to get the new OpgaveID

            ressources = session.query(Ressource).filter_by(OpgaveID=opgave.OpgaveID).all()
            for ressource in ressources:
                new_ressource = Ressource(
                    name=ressource.name,
                    url=ressource.url,
                    OpgaveID=new_opgave.OpgaveID  # Use the new OpgaveID
                )
                session.add(new_ressource)
            session.commit()

        return jsonify({"message": "Forløb preparation created successfully with template", "uid": forloeb.ForløbID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def start_preparation_forloeb():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['ForløbID', 'startdate', 'enddate', 'planMails']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        forloeb = session.query(Forløb).filter_by(ForløbID=data['ForløbID'], isPreparation=True).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found or not in preparation mode"}), 404

        forloeb.startdate = datetime.fromisoformat(data['startdate'])
        forloeb.enddate = datetime.fromisoformat(data['enddate']) if 'enddate' in data else forloeb.startdate + timedelta(days=forloeb.varighed)
        forloeb.isPreparation = False
        session.commit()

        for opgave in forloeb.opgave:
            opgave.startdato = forloeb.startdate + timedelta(days=opgave.relativ_startdag)
            opgave.slutdato = opgave.startdato + timedelta(days=opgave.relativ_slutdag)
            session.commit()

            # Optionally send plan mails
            if opgave.ansvarligEmail and data.get('planMails') is True:
                subject, message = create_mail_ansvarlig(opgave)
                plan_mail(opgave.ansvarligEmail, subject, message, opgave_id=opgave.OpgaveID)

        if data.get('planWelcome') is True:
            subject, message = create_mail_forloeb_start(forloeb)
            plan_mail(forloeb.usermail, subject, message, forloeb_id=forloeb.ForløbID)

        return jsonify({"message": "Forløb started successfully", "startdate": forloeb.startdate.isoformat(), "enddate": forloeb.enddate.isoformat(), "uid": forloeb.ForløbID}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloeb(forloeb_id: int):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        opgave_grupper = session.query(OpgaveGruppe).filter_by(ForløbID=forloeb.ForløbID).all()

        result = {
            "ForløbID": forloeb.ForløbID,
            "name": forloeb.name,
            "startdate": forloeb.startdate.isoformat() if forloeb.startdate else None,
            "enddate": forloeb.enddate.isoformat() if forloeb.enddate else None,
            "admin": forloeb.admin,
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
            "pending_emails": [
                {
                    "id": mail.MailID,
                    "recipient": mail.recipient,
                    "subject": mail.subject
                } for mail in forloeb.mails if not mail.isSent
            ]
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_all_forloeb():
    session = db_client.get_session()
    try:
        forloeb_list = session.query(Forløb).all()
        result = [
            {
                "ForløbID": forloeb.ForløbID,
                "name": forloeb.name,
                "startdate": forloeb.startdate.isoformat() if forloeb.startdate else None,
                "enddate": forloeb.enddate.isoformat() if forloeb.enddate else None,
                "admin": forloeb.admin,
                "usermail": forloeb.usermail,
                "userdq": forloeb.userdq,
                "isPreparation": forloeb.isPreparation,
                "varighed": forloeb.varighed
            }
            for forloeb in forloeb_list
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloeb_with_opgaver():
    session = db_client.get_session()
    try:
        forloeb_list = session.query(Forløb).join(Opgave).all()
        forloeb_data = [
            {
                'ForløbID': forloeb.ForløbID,
                'name': forloeb.name,
                'isPreparation': forloeb.isPreparation,
                'varighed': forloeb.varighed
            } for forloeb in forloeb_list
        ]
        return jsonify(forloeb_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloeb_by_email(mail):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter(Forløb.usermail.ilike(mail.lower())).first()
        if not forloeb:
            return jsonify(None), 200

        opgave_grupper = session.query(OpgaveGruppe).filter_by(ForløbID=forloeb.ForløbID).all()

        result = {
            "ForløbID": forloeb.ForløbID,
            "name": forloeb.name,
            "startdate": forloeb.startdate.isoformat() if forloeb.startdate else None,
            "enddate": forloeb.enddate.isoformat() if forloeb.enddate else None,
            "admin": forloeb.admin,
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
            "varighed": forloeb.varighed
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloeb_by_admin(admin_name):
    session = db_client.get_session()
    try:
        forloeb_list = (
            session.query(Forløb)
            .options(
                selectinload(Forløb.opgave_grupper),
                selectinload(Forløb.mails),
            )
            .filter_by(admin=admin_name)
            .all()
        )
        if not forloeb_list:
            return jsonify([]), 200

        result = []
        for forloeb in forloeb_list:
            result.append(
                {
                    "ForløbID": forloeb.ForløbID,
                    "name": forloeb.name,
                    "startdate": forloeb.startdate.isoformat() if forloeb.startdate else None,
                    "enddate": forloeb.enddate.isoformat() if forloeb.enddate else None,
                    "admin": forloeb.admin,
                    "usermail": forloeb.usermail,
                    "userdq": forloeb.userdq,
                    "opgave_grupper": [
                        {
                            "OpgaveGruppeID": gruppe.OpgaveGruppeID,
                            "name": gruppe.name,
                            "letter": gruppe.letter,
                        }
                        for gruppe in forloeb.opgave_grupper
                    ],
                    "isPreparation": forloeb.isPreparation,
                    "varighed": forloeb.varighed,
                    "pending_emails": [
                        {
                            "id": mail.MailID,
                            "recipient": mail.recipient,
                            "subject": mail.subject
                        } for mail in forloeb.mails if not mail.isSent
                    ]
                }
            )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_forloeb(id):
    data = request.json
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        forloeb.name = data.get('name', forloeb.name)
        if data.get('startdate'):
            forloeb.startdate = datetime.fromisoformat(data['startdate'])
        if data.get('enddate'):
            forloeb.enddate = datetime.fromisoformat(data['enddate'])
        forloeb.admin = data.get('admin', forloeb.admin)
        forloeb.usermail = data.get('usermail', forloeb.usermail)
        forloeb.userdq = data.get('userdq', forloeb.userdq)

        if len(forloeb.mails) == 0 or all(mail.isSent for mail in forloeb.mails):
            if data.get('planWelcome') is True:
                subject, message = create_mail_forloeb_start(forloeb)
                plan_mail(forloeb.usermail, subject, message, forloeb_id=forloeb.ForløbID)

        session.commit()
        return jsonify({"message": "Forløb updated successfully", "uid": forloeb.ForløbID}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def complete_forloeb(id):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        forloeb.enddate = datetime.now()
        session.commit()
        return jsonify({"message": "Forløb completed successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def delete_forloeb(id):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        session.delete(forloeb)
        session.commit()
        return jsonify({"message": "Forløb deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

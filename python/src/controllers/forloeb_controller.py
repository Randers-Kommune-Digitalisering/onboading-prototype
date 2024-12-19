from flask import request, jsonify
from datetime import datetime
from models import Forløb, Forløbsskabelon, Opgave
from utils.db_connection import get_db_client
import logging


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
            userdq=data['userdq']
        )
        session.add(forloeb)
        session.commit()

        if 'ForløbsskabelonID' in data:
            forløbsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=data['ForløbsskabelonID']).first()
            if not forløbsskabelon:
                return jsonify({"error": "Forløbsskabelon not found"}), 404

            for opgave in forløbsskabelon.opgave:
                new_opgave = Opgave(
                    title=opgave.title,
                    beskrivelse=opgave.beskrivelse,
                    ansvarlig=opgave.ansvarlig,
                    startdato=opgave.startdato,
                    slutdato=opgave.slutdato,
                    result=opgave.result,
                    timestamp=opgave.timestamp,
                    ForløbID=forloeb.ForløbID
                )
                session.add(new_opgave)
            session.commit()

        return jsonify({"message": "Forløb created successfully"}), 201
    except Exception as e:
        session.rollback()
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
                "startdate": forloeb.startdate.isoformat(),
                "enddate": forloeb.enddate.isoformat(),
                "admin": forloeb.admin,
                "usermail": forloeb.usermail,
                "userdq": forloeb.userdq
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
                'name': forloeb.name
            } for forloeb in forloeb_list
        ]
        return jsonify(forloeb_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

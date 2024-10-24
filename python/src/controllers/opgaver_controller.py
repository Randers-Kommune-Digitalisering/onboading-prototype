from flask import request, jsonify
from datetime import datetime
from models import Opgaver
from utils.database import DatabaseClient
from utils.config import MSSQL_USER, MSSQL_PASS, MSSQL_HOST, MSSQL_DATABASE

db_client = DatabaseClient('mssql', MSSQL_DATABASE, MSSQL_USER, MSSQL_PASS, MSSQL_HOST)


def create_opgaver_with_forloebs_id():
    session = db_client.get_session()
    try:
        data = request.json
        if 'ForløbsskabelonID' not in data:
            return jsonify({"error": "Missing required field: ForløbsskabelonID"}), 400

        opgave = Opgaver(
            title=data['title'],
            beskrivelse=data['beskrivelse'],
            resourcer=data['resourcer'],
            ansvarlig=data['ansvarlig'],
            startdato=datetime.fromisoformat(data['startdato']),
            slutdato=datetime.fromisoformat(data['slutdato']),
            result=data['result'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            ForløbsskabelonID=data['ForløbsskabelonID']
        )
        session.add(opgave)
        session.commit()
        return jsonify({"message": "Opgaver created successfully with ForløbsskabelonID"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_all_opgaver():
    session = db_client.get_session()
    try:
        opgaver = session.query(Opgaver).all()
        opgaver_data = [
            {
                'OpgaverID': opgave.OpgaverID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': opgave.resourcer,
                'ansvarlig': opgave.ansvarlig,
                'startdato': opgave.startdato.isoformat(),
                'slutdato': opgave.slutdato.isoformat(),
                'result': opgave.result,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgaver
        ]
        return jsonify(opgaver_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgaver_by_forloebsskabelon_id(forlobsskabelon_id):
    session = db_client.get_session()
    try:
        opgaver = session.query(Opgaver).filter_by(ForløbsskabelonID=forlobsskabelon_id).all()
        if not opgaver:
            return jsonify({"error": "No opgaver found for the specified ForløbsskabelonID"}), 404

        opgaver_data = [
            {
                'OpgaverID': opgave.OpgaverID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': opgave.resourcer,
                'ansvarlig': opgave.ansvarlig,
                'startdato': opgave.startdato.isoformat(),
                'slutdato': opgave.slutdato.isoformat(),
                'result': opgave.result,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgaver
        ]
        return jsonify(opgaver_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_opgaver(opgave_id):
    session = db_client.get_session()
    try:
        data = request.json

        opgave = session.query(Opgaver).filter_by(OpgaverID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgaver not found"}), 404

        opgave.title = data.get('title', opgave.title)
        opgave.beskrivelse = data.get('beskrivelse', opgave.beskrivelse)
        opgave.resourcer = data.get('resourcer', opgave.resourcer)
        opgave.ansvarlig = data.get('ansvarlig', opgave.ansvarlig)
        opgave.startdato = datetime.fromisoformat(data['startdato']) if 'startdato' in data else opgave.startdato
        opgave.slutdato = datetime.fromisoformat(data['slutdato']) if 'slutdato' in data else opgave.slutdato
        opgave.result = data.get('result', opgave.result)
        opgave.timestamp = datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else opgave.timestamp

        session.commit()
        return jsonify({"message": "Opgaver updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def delete_opgaver(opgave_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgaver).filter_by(OpgaverID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgaver not found"}), 404

        session.delete(opgave)
        session.commit()
        return jsonify({"message": "Opgaver deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

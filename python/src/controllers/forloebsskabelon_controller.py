from flask import request, jsonify
from datetime import datetime
from models import Forløbsskabelon
from utils.db_connection import get_db_client

db_client = get_db_client()


def create_forloebsskabelon():
    session = db_client.get_session()
    try:
        data = request.json
        if 'name' not in data or 'varighed' not in data:
            return jsonify({"error": "Missing required fields: name and varighed"}), 400

        forloebsskabelon = Forløbsskabelon(
            name=data['name'],
            varighed=datetime.fromisoformat(data['varighed'])
        )
        session.add(forloebsskabelon)
        session.commit()
        return jsonify({"message": "Forløbsskabelon created successfully"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_all_forloebsskabeloner():
    session = db_client.get_session()
    try:
        forloebsskabeloner = session.query(Forløbsskabelon).all()
        forloebsskabeloner_data = [
            {
                'ForløbsskabelonID': forloebsskabelon.ForløbsskabelonID,
                'name': forloebsskabelon.name,
                'varighed': forloebsskabelon.varighed.isoformat()
            } for forloebsskabelon in forloebsskabeloner
        ]
        return jsonify(forloebsskabeloner_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_forloebsskabelon_name(forloebsskabelon_id):
    session = db_client.get_session()
    try:
        data = request.json
        if 'name' not in data:
            return jsonify({"error": "Missing required field: name"}), 400

        forloebsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=forloebsskabelon_id).first()
        if not forloebsskabelon:
            return jsonify({"error": "Forløbsskabelon not found"}), 404

        forloebsskabelon.name = data['name']
        session.commit()
        return jsonify({"message": "Forløbsskabelon name updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

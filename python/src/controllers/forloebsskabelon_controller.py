from flask import request, jsonify
from models import Forløbsskabelon, Opgave
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
            varighed=data['varighed']
        )
        session.add(forloebsskabelon)
        session.commit()
        return jsonify({"message": "Forløbsskabelon created successfully", "uid": forloebsskabelon.ForløbsskabelonID}), 201
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
                'varighed': forloebsskabelon.varighed
            } for forloebsskabelon in forloebsskabeloner
        ]
        return jsonify(forloebsskabeloner_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloebsskabelon_by_id(forloebsskabelon_id):
    session = db_client.get_session()
    try:
        forloebsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=forloebsskabelon_id).first()
        if not forloebsskabelon:
            return jsonify({"error": "Forløbsskabelon not found"}), 404

        forloebsskabelon_data = {
            'ForløbsskabelonID': forloebsskabelon.ForløbsskabelonID,
            'name': forloebsskabelon.name,
            'varighed': forloebsskabelon.varighed
        }
        return jsonify(forloebsskabelon_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_forloebsskabelon(forloebsskabelon_id):
    session = db_client.get_session()
    try:
        data = request.json

        forloebsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=forloebsskabelon_id).first()
        if not forloebsskabelon:
            return jsonify({"error": "Forløbsskabelon not found"}), 404

        forloebsskabelon.name = data.get('name', forloebsskabelon.name)
        forloebsskabelon.varighed = data.get('varighed', forloebsskabelon.varighed)

        session.commit()
        return jsonify({"message": "Forløbsskabelon updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloebsskabeloner_with_opgaver():
    session = db_client.get_session()
    try:
        forloebsskabeloner = session.query(Forløbsskabelon).join(Opgave).all()
        forloebsskabeloner_data = [
            {
                'ForløbsskabelonID': forloebsskabelon.ForløbsskabelonID,
                'name': forloebsskabelon.name
            } for forloebsskabelon in forloebsskabeloner
        ]
        return jsonify(forloebsskabeloner_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

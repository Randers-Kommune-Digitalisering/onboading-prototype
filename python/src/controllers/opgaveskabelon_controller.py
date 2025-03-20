from flask import request, jsonify
from models import Opgaveskabelon
from utils.db_connection import get_db_client

db_client = get_db_client()


def create_opgaveskabelon():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['title', 'beskrivelse', 'relativ_slutdag']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_opgaveskabelon = Opgaveskabelon(
            title=data['title'],
            beskrivelse=data['beskrivelse'],
            relativ_slutdag=data['relativ_slutdag'],
        )
        session.add(new_opgaveskabelon)
        session.commit()
        return jsonify({"message": "Opgaveskabelon created successfully"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_all_opgaveskabeloner():
    session = db_client.get_session()
    try:
        opgaveskabeloner = session.query(Opgaveskabelon).all()
        opgaveskabeloner_data = [
            {
                'OpgaveskabelonID': opgaveskabelon.OpgaveskabelonID,
                'title': opgaveskabelon.title,
                'beskrivelse': opgaveskabelon.beskrivelse,
                'relativ_slutdag': opgaveskabelon.relativ_slutdag
            } for opgaveskabelon in opgaveskabeloner
        ]
        return jsonify(opgaveskabeloner_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_opgaveskabelon(opgaveskabelon_id):
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['title', 'beskrivelse', 'relativ_slutdag']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=opgaveskabelon_id).first()
        if not opgaveskabelon:
            return jsonify({"error": "Opgaveskabelon not found"}), 404

        opgaveskabelon.title = data['title']
        opgaveskabelon.beskrivelse = data['beskrivelse']
        opgaveskabelon.relativ_slutdag = data['relativ_slutdag']

        session.commit()
        return jsonify({"message": "Opgaveskabelon updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def delete_opgaveskabelon(opgaveskabelon_id):
    session = db_client.get_session()
    try:
        opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=opgaveskabelon_id).first()
        if not opgaveskabelon:
            return jsonify({"error": "Opgaveskabelon not found"}), 404

        session.delete(opgaveskabelon)
        session.commit()
        return jsonify({"message": "Opgaveskabelon deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

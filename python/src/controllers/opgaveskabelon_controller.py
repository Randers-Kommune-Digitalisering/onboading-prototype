from flask import request, jsonify
from models import Opgaveskabelon, Ressource, RessourceFile
from utils.db_connection import get_db_client
from utils.ressource_serialization import serialize_ressource
from sqlalchemy.orm import selectinload

db_client = get_db_client()


def create_opgaveskabelon():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['beskrivelse', 'relativ_slutdag']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_opgaveskabelon = Opgaveskabelon(
            title=data.get('title', ''),
            beskrivelse=data['beskrivelse'],
            note=data['note'],
            hidden=bool(data.get('hidden', False)),
            relativ_slutdag=data['relativ_slutdag'],
        )
        session.add(new_opgaveskabelon)
        session.commit()
        return jsonify({"message": "Opgaveskabelon created successfully", "OpgaveID": new_opgaveskabelon.OpgaveskabelonID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_all_opgaveskabeloner():
    session = db_client.get_session()
    try:
        opgaveskabeloner = (
            session.query(Opgaveskabelon)
            .options(selectinload(Opgaveskabelon.ressource).selectinload(Ressource.file).defer(RessourceFile.data))
            .all()
        )
        opgaveskabeloner_data = [
            {
                'OpgaveskabelonID': opgaveskabelon.OpgaveskabelonID,
                'title': opgaveskabelon.title,
                'beskrivelse': opgaveskabelon.beskrivelse,
                'relativ_slutdag': opgaveskabelon.relativ_slutdag,
                'note': opgaveskabelon.note if opgaveskabelon.note else "",
                'hidden': bool(getattr(opgaveskabelon, 'hidden', False)),
                'resourcer': [serialize_ressource(ressource) for ressource in opgaveskabelon.ressource]
            } for opgaveskabelon in opgaveskabeloner
        ]
        return jsonify(opgaveskabeloner_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgaveskabelon(opgaveskabelon_id):
    session = db_client.get_session()
    try:
        opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=opgaveskabelon_id).first()
        if not opgaveskabelon:
            return jsonify({"error": "Opgaveskabelon not found"}), 404

        opgaveskabelon_data = {
            'OpgaveskabelonID': opgaveskabelon.OpgaveskabelonID,
            'title': opgaveskabelon.title,
            'beskrivelse': opgaveskabelon.beskrivelse,
            'note': opgaveskabelon.note if opgaveskabelon.note else "",
            'hidden': bool(getattr(opgaveskabelon, 'hidden', False)),
            'relativ_slutdag': opgaveskabelon.relativ_slutdag
        }
        return jsonify(opgaveskabelon_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_opgaveskabelon(opgaveskabelon_id):
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['beskrivelse', 'relativ_slutdag']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=opgaveskabelon_id).first()
        if not opgaveskabelon:
            return jsonify({"error": "Opgaveskabelon not found"}), 404

        opgaveskabelon.title = data.get('title', opgaveskabelon.title)
        opgaveskabelon.beskrivelse = data['beskrivelse']
        opgaveskabelon.note = data['note']
        opgaveskabelon.hidden = bool(data.get('hidden', False))
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

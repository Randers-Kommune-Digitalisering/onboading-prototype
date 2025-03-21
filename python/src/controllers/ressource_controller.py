from flask import request, jsonify
from models import Ressource, Opgave, Opgaveskabelon
from utils.db_connection import get_db_client

db_client = get_db_client()


def create_ressource():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['name', 'url']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_ressource = Ressource(
            name=data['name'],
            url=data['url']
        )

        if 'OpgaveID' in data:
            opgave = session.query(Opgave).filter_by(OpgaveID=data['OpgaveID']).first()
            if not opgave:
                return jsonify({"error": "Opgave not found"}), 404
            new_ressource.OpgaveID = opgave.OpgaveID
        elif 'OpgaveskabelonID' in data:
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

        data = request.json
        ressource.name = data.get('name', ressource.name)
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
        ressource = session.query(Ressource).filter_by(RessourceID=ressource_id).first()
        if not ressource:
            return jsonify({"error": "Ressource not found"}), 404

        result = {
            "RessourceID": ressource.RessourceID,
            "name": ressource.name,
            "url": ressource.url
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_ressources_by_opgaveid(opgave_id):
    session = db_client.get_session()
    try:
        ressources = session.query(Ressource).filter_by(OpgaveID=opgave_id).all()
        if not ressources:
            return jsonify({"error": "No ressources found for the specified OpgaveID"}), 404

        ressource_data = [
            {
                'RessourceID': ressource.RessourceID,
                'name': ressource.name,
                'url': ressource.url
            } for ressource in ressources
        ]
        return jsonify(ressource_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_ressources_by_opgaveskabelonid(opgaveskabelon_id):
    session = db_client.get_session()
    try:
        ressources = session.query(Ressource).filter_by(OpgaveskabelonID=opgaveskabelon_id).all()
        if not ressources:
            return jsonify({"error": "No ressources found for the specified OpgaveskabelonID"}), 404

        ressource_data = [
            {
                'RessourceID': ressource.RessourceID,
                'name': ressource.name,
                'url': ressource.url
            } for ressource in ressources
        ]
        return jsonify(ressource_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

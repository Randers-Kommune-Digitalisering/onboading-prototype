import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from models.opgaver import Opgaver, Base as BaseOpgaver
from models.forloebsskabeloner import Forloebsskabeloner, Base as BaseForloebsskabeloner
from utils.database import DatabaseClient
from utils.config import MSSQL_USER, MSSQL_PASS, MSSQL_HOST, MSSQL_DATABASE


db_client = DatabaseClient('mssql', MSSQL_DATABASE, MSSQL_USER, MSSQL_PASS, MSSQL_HOST)

BaseOpgaver.metadata.create_all(db_client.engine)
BaseForloebsskabeloner.metadata.create_all(db_client.engine)

logger = logging.getLogger(__name__)
api_endpoints = Blueprint('api', __name__, url_prefix='/api')


@api_endpoints.route('/opgaver', methods=['GET'])
def get_opgaver():
    session = db_client.get_session()
    try:
        rows = session.query(Opgaver).all()
        result = []
        for row in rows:
            result.append({
                'OpgaverID': row.OpgaverID,
                'title': row.title,
                'beskrivelse': row.beskrivelse,
                'resourcer': row.resourcer,
                'ansvarlig': row.ansvarlig,
                'startdato': row.startdato.isoformat(),
                'slutdato': row.slutdato.isoformat()
            })
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        return jsonify({"error": "Error retrieving data"}), 500
    finally:
        session.close()


@api_endpoints.route('/opgaver', methods=['POST'])
def add_opgave():
    session = db_client.get_session()
    try:
        data = request.json
        title = data.get('title')
        beskrivelse = data.get('beskrivelse')
        resourcer = data.get('resourcer')
        ansvarlig = data.get('ansvarlig')
        startdato = data.get('startdato')
        slutdato = data.get('slutdato')

        if not all([title, beskrivelse, resourcer, ansvarlig, startdato, slutdato]):
            return jsonify({"error": "Missing required fields"}), 400

        new_opgave = Opgaver(
            title=title,
            beskrivelse=beskrivelse,
            resourcer=resourcer,
            ansvarlig=ansvarlig,
            startdato=datetime.fromisoformat(startdato),
            slutdato=datetime.fromisoformat(slutdato)
        )

        session.add(new_opgave)
        session.commit()
        return jsonify({"message": "Task added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        session.rollback()
        return jsonify({"error": "Error adding task"}), 500
    finally:
        session.close()

@api_endpoints.route('/opgaver/<int:opgave_id>', methods=['DELETE'])
def delete_opgave(opgave_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgaver).filter(Opgaver.OpgaverID == opgave_id).one_or_none()
        if opgave is None:
            return jsonify({"error": "Task not found"}), 404

        session.delete(opgave)
        session.commit()
        return jsonify({"message": "Task deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        session.rollback()
        return jsonify({"error": "Error deleting task"}), 500
    finally:
        session.close()


@api_endpoints.route('/opgaver/<int:opgave_id>', methods=['PUT'])
def update_opgave(opgave_id):
    session = db_client.get_session()
    try:
        data = request.json
        opgave = session.query(Opgaver).filter(Opgaver.OpgaverID == opgave_id).one_or_none()
        if opgave is None:
            return jsonify({"error": "Task not found"}), 404

        opgave.title = data.get('title', opgave.title)
        opgave.beskrivelse = data.get('beskrivelse', opgave.beskrivelse)
        opgave.resourcer = data.get('resourcer', opgave.resourcer)
        opgave.ansvarlig = data.get('ansvarlig', opgave.ansvarlig)
        opgave.startdato = datetime.fromisoformat(data.get('startdato', opgave.startdato.isoformat()))
        opgave.slutdato = datetime.fromisoformat(data.get('slutdato', opgave.slutdato.isoformat()))

        session.commit()
        return jsonify({"message": "Task updated successfully"})
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        session.rollback()
        return jsonify({"error": "Error updating task"}), 500
    finally:
        session.close()

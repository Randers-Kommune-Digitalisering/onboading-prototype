from flask import request, jsonify
from datetime import datetime
from models.forloebsskabeloner import Forløbsskabelon
from utils.database import DatabaseClient
from utils.config import MSSQL_USER, MSSQL_PASS, MSSQL_HOST, MSSQL_DATABASE

db_client = DatabaseClient('mssql', MSSQL_DATABASE, MSSQL_USER, MSSQL_PASS, MSSQL_HOST)


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

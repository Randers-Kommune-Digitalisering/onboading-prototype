from flask import request, jsonify
from datetime import datetime
from models import Opgave, Forløb, Forløbsskabelon, Opgaveskabelon, Ressource
from utils.db_connection import get_db_client

db_client = get_db_client()


def create_opgave():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['title', 'beskrivelse', 'ansvarlig', 'ansvarligEmail', 'result', 'timestamp']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        new_opgave = Opgave(
            title=data['title'],
            beskrivelse=data['beskrivelse'],
            ansvarlig=data['ansvarlig'],
            ansvarligEmail=data['ansvarligEmail'],
            startdato=datetime.fromisoformat(data['startdato']) if 'startdato' in data else None,
            slutdato=datetime.fromisoformat(data['slutdato']) if 'slutdato' in data else None,
            relativ_startdag=data['relativ_startdag'] if 'relativ_startdag' in data else None,
            relativ_slutdag=data['relativ_slutdag'] if 'relativ_slutdag' in data else None,
            result=data['result'],
            booking=datetime.fromisoformat(data['booking']) if 'booking' in data else None,
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        )

        if 'ForløbID' in data:
            forløb = session.query(Forløb).filter_by(ForløbID=data['ForløbID']).first()
            if not forløb:
                return jsonify({"error": "Forløb not found"}), 404
            new_opgave.forløb = forløb
        elif 'ForløbsskabelonID' in data:
            forløbsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=data['ForløbsskabelonID']).first()
            if not forløbsskabelon:
                return jsonify({"error": "Forløbsskabelon not found"}), 404
            new_opgave.forløbsskabelon = forløbsskabelon

            print(f"relativ_startdag: {new_opgave.relativ_startdag}, relativ_slutdag: {new_opgave.relativ_slutdag}")
            if 'relativ_startdag' not in data or 'relativ_slutdag' not in data:
                return jsonify({"error": "relativ_startdag and relativ_slutdag are required to create new opgaveskabelon"}), 400
        else:
            return jsonify({"error": "Either ForløbID or ForløbsskabelonID is required"}), 400

        session.add(new_opgave)
        session.commit()
        return jsonify({"message": "Opgave created successfully", "OpgaveID": new_opgave.OpgaveID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_all_opgaver():
    session = db_client.get_session()
    try:
        opgaver = session.query(Opgave).all()
        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [
                    {
                        'RessourceID': ressource.RessourceID,
                        'name': ressource.name,
                        'url': ressource.url
                    } for ressource in opgave.ressource
                ],
                'ansvarlig': opgave.ansvarlig,
                'ansvarligEmail': opgave.ansvarligEmail,
                'startdato': opgave.startdato.isoformat() if opgave.startdato else None,
                'slutdato': opgave.slutdato.isoformat() if opgave.slutdato else None,
                'relativ_startdag': opgave.relativ_startdag,
                'relativ_slutdag': opgave.relativ_slutdag,
                'result': opgave.result,
                'booking': opgave.booking.isoformat() if opgave.booking else None,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgaver
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def create_opgave_with_opgaveskabelon():
    session = db_client.get_session()
    try:
        data = request.json
        required_fields = ['OpgaveskabelonID']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        opgaveskabelon = session.query(Opgaveskabelon).filter_by(OpgaveskabelonID=data['OpgaveskabelonID']).first()
        if not opgaveskabelon:
            return jsonify({"error": "Opgaveskabelon not found"}), 404

        new_opgave = Opgave(
            title=data.get('title', opgaveskabelon.title),
            beskrivelse=data.get('beskrivelse', opgaveskabelon.beskrivelse),
            ansvarlig=data.get('ansvarlig', ""),
            ansvarligEmail=data.get('ansvarligEmail', ""),
            startdato=datetime.fromisoformat(data['startdato']) if 'startdato' in data else None,
            slutdato=datetime.fromisoformat(data['slutdato']) if 'slutdato' in data else None,
            relativ_startdag=data['relativ_startdag'] if 'relativ_startdag' in data else None,
            relativ_slutdag=data['relativ_slutdag'] if 'relativ_slutdag' in data else None,
            result=data.get('result', False),
            timestamp=datetime.now()
        )

        if 'ForløbID' in data:
            forløb = session.query(Forløb).filter_by(ForløbID=data['ForløbID']).first()
            if not forløb:
                return jsonify({"error": "Forløb not found"}), 404
            new_opgave.forløb = forløb
        elif 'ForløbsskabelonID' in data:
            forløbsskabelon = session.query(Forløbsskabelon).filter_by(ForløbsskabelonID=data['ForløbsskabelonID']).first()
            if not forløbsskabelon:
                return jsonify({"error": "Forløbsskabelon not found"}), 404
            new_opgave.forløbsskabelon = forløbsskabelon
        else:
            return jsonify({"error": "Either ForløbID or ForløbsskabelonID is required"}), 400

        session.add(new_opgave)
        session.commit()

        for ressource in opgaveskabelon.ressource:
            new_ressource = Ressource(
                name=ressource.name,
                url=ressource.url,
                OpgaveID=new_opgave.OpgaveID
            )
            session.add(new_ressource)
        session.commit()

        return jsonify({"message": "Opgave created successfully with Opgaveskabelon", "OpgaveID": new_opgave.OpgaveID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloebsskabelon_id(forlobsskabelon_id):
    session = db_client.get_session()
    try:
        usermail = request.headers.get('usermail')

        query = session.query(Opgave).join(Forløb).filter(Opgave.ForløbsskabelonID == forlobsskabelon_id)
        if usermail:
            query = query.filter(Forløb.usermail == usermail)

        opgave = query.all()

        if not opgave:
            return jsonify({"error": "No opgave found for the specified ForløbsskabelonID and usermail"}), 404

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [
                    {
                        'RessourceID': ressource.RessourceID,
                        'name': ressource.name,
                        'url': ressource.url
                    } for ressource in opgave.ressource
                ],
                'ansvarlig': opgave.ansvarlig,
                'ansvarligEmail': opgave.ansvarligEmail,
                'startdato': opgave.startdato.isoformat() if opgave.startdato else None,
                'slutdato': opgave.slutdato.isoformat() if opgave.slutdato else None,
                'relativ_startdag': opgave.relativ_startdag,
                'relativ_slutdag': opgave.relativ_slutdag,
                'result': opgave.result,
                'booking': opgave.booking.isoformat() if opgave.booking else None,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave(opgave_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgave).filter_by(OpgaveID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgave not found"}), 404

        opgave_data = {
            'OpgaveID': opgave.OpgaveID,
            'title': opgave.title,
            'beskrivelse': opgave.beskrivelse,
            'resourcer': [
                {
                    'RessourceID': ressource.RessourceID,
                    'name': ressource.name,
                    'url': ressource.url
                } for ressource in opgave.ressource
            ],
            'ansvarlig': opgave.ansvarlig,
            'ansvarligEmail': opgave.ansvarligEmail,
            'startdato': opgave.startdato.isoformat() if opgave.startdato else None,
            'slutdato': opgave.slutdato.isoformat() if opgave.slutdato else None,
            'relativ_startdag': opgave.relativ_startdag,
            'relativ_slutdag': opgave.relativ_slutdag,
            'result': opgave.result,
            'booking': opgave.booking.isoformat() if opgave.booking else None,
            'timestamp': opgave.timestamp.isoformat(),
            'ForløbID': opgave.ForløbID,
            'ForløbsskabelonID': opgave.ForløbsskabelonID
        }
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloebsskabelon_id_admin(forlobsskabelon_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgave).filter_by(ForløbsskabelonID=forlobsskabelon_id).all()
        if not opgave:
            return jsonify({"error": "No opgave found for the specified ForløbsskabelonID"}), 404

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [
                    {
                        'RessourceID': ressource.RessourceID,
                        'name': ressource.name,
                        'url': ressource.url
                    } for ressource in opgave.ressource
                ],
                'ansvarlig': opgave.ansvarlig,
                'ansvarligEmail': opgave.ansvarligEmail,
                'startdato': opgave.startdato.isoformat() if opgave.startdato else None,
                'slutdato': opgave.slutdato.isoformat() if opgave.slutdato else None,
                'relativ_startdag': opgave.relativ_startdag,
                'relativ_slutdag': opgave.relativ_slutdag,
                'result': opgave.result,
                'booking': opgave.booking.isoformat() if opgave.booking else None,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloeb_id_admin(forlob_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgave).filter_by(ForløbID=forlob_id).all()
        if not opgave:
            return jsonify({"error": "No opgave found for the specified ForløbID"}), 404

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [
                    {
                        'RessourceID': ressource.RessourceID,
                        'name': ressource.name,
                        'url': ressource.url
                    } for ressource in opgave.ressource
                ],
                'ansvarlig': opgave.ansvarlig,
                'ansvarligEmail': opgave.ansvarligEmail,
                'startdato': opgave.startdato.isoformat(),
                'slutdato': opgave.slutdato.isoformat(),
                'relativ_startdag': opgave.relativ_startdag,
                'relativ_slutdag': opgave.relativ_slutdag,
                'result': opgave.result,
                'booking': opgave.booking.isoformat() if opgave.booking else None,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_admin(adminmail):  # Admin = ansvarlig in this case, bad naming
    session = db_client.get_session()
    try:
        query = session.query(Opgave).filter(Opgave.ansvarligEmail == adminmail)
        opgave = query.all()

        if not opgave:
            return jsonify({"error": "No opgave found for the specified usermail"}), 404

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'ForløbID': opgave.ForløbID,
                'ForløbsskabelonID': opgave.ForløbsskabelonID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [
                    {
                        'RessourceID': ressource.RessourceID,
                        'name': ressource.name,
                        'url': ressource.url
                    } for ressource in opgave.ressource
                ],
                'ansvarlig': opgave.ansvarlig,
                'ansvarligEmail': opgave.ansvarligEmail,
                'startdato': opgave.startdato.isoformat(),
                'slutdato': opgave.slutdato.isoformat(),
                'relativ_startdag': opgave.relativ_startdag,
                'relativ_slutdag': opgave.relativ_slutdag,
                'result': opgave.result,
                'booking': opgave.booking.isoformat() if opgave.booking else None,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_opgave_by_forloeb_id(forlob_id):
    session = db_client.get_session()
    try:
        usermail = request.headers.get('usermail')

        query = session.query(Opgave).join(Forløb).filter(Opgave.ForløbID == forlob_id)
        if usermail:
            query = query.filter(Forløb.usermail == usermail)

        opgave = query.all()

        if not opgave:
            return jsonify({"error": "No opgave found for the specified ForløbID and usermail"}), 404

        opgave_data = [
            {
                'OpgaveID': opgave.OpgaveID,
                'title': opgave.title,
                'beskrivelse': opgave.beskrivelse,
                'resourcer': [
                    {
                        'RessourceID': ressource.RessourceID,
                        'name': ressource.name,
                        'url': ressource.url
                    } for ressource in opgave.ressource
                ],
                'ansvarlig': opgave.ansvarlig,
                'ansvarligEmail': opgave.ansvarligEmail,
                'startdato': opgave.startdato.isoformat() if opgave.startdato else None,
                'slutdato': opgave.slutdato.isoformat() if opgave.slutdato else None,
                'relativ_startdag': opgave.relativ_startdag,
                'relativ_slutdag': opgave.relativ_slutdag,
                'result': opgave.result,
                'booking': opgave.booking.isoformat() if opgave.booking else None,
                'timestamp': opgave.timestamp.isoformat()
            } for opgave in opgave
        ]
        return jsonify(opgave_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def update_opgave(opgave_id):
    session = db_client.get_session()
    try:
        data = request.json

        opgave = session.query(Opgave).filter_by(OpgaveID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgave not found"}), 404

        opgave.title = data.get('title', opgave.title)
        opgave.beskrivelse = data.get('beskrivelse', opgave.beskrivelse)
        opgave.ansvarlig = data.get('ansvarlig', opgave.ansvarlig)
        opgave.ansvarligEmail = data.get('ansvarligEmail', opgave.ansvarligEmail)
        opgave.startdato = datetime.fromisoformat(data['startdato']) if 'startdato' in data else opgave.startdato
        opgave.slutdato = datetime.fromisoformat(data['slutdato']) if 'slutdato' in data else opgave.slutdato
        opgave.relativ_startdag = data.get('relativ_startdag', opgave.relativ_startdag)
        opgave.relativ_slutdag = data.get('relativ_slutdag', opgave.relativ_slutdag)
        opgave.result = data.get('result', opgave.result)
        opgave.booking = datetime.fromisoformat(data['booking']) if 'booking' in data else opgave.booking,
        opgave.timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')) if 'timestamp' in data else opgave.timestamp

        session.commit()
        return jsonify({"message": "Opgave updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def delete_opgave(opgave_id):
    session = db_client.get_session()
    try:
        opgave = session.query(Opgave).filter_by(OpgaveID=opgave_id).first()
        if not opgave:
            return jsonify({"error": "Opgave not found"}), 404

        session.delete(opgave)
        session.commit()
        return jsonify({"message": "Opgave deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

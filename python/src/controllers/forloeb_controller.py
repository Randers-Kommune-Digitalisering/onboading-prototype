from flask import make_response, request, jsonify
from fpdf import FPDF
from datetime import datetime, timedelta
from models import Forløb, Forløbsskabelon, Opgave, Ressource
from utils.db_connection import get_db_client
import logging
from controllers.opgave_controller import get_opgave_by_forloeb_id

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
                    startdato=forloeb.startdate + timedelta(days=opgave.relativ_startdag),  # Adding relative days
                    slutdato=forloeb.startdate + timedelta(days=opgave.relativ_startdag) + timedelta(days=opgave.relativ_slutdag),
                    result=opgave.result,
                    timestamp=opgave.timestamp,
                    ForløbID=forloeb.ForløbID
                )
                session.add(new_opgave)
                session.commit()  # Commit to get the new OpgaveID

                ressources = session.query(Ressource).filter_by(OpgaveID=opgave.OpgaveID).all()
                for ressource in ressources:
                    new_ressource = Ressource(
                        name=ressource.name,
                        url=ressource.url,
                        OpgaveID=new_opgave.OpgaveID  # Use the new OpgaveID
                    )
                    session.add(new_ressource)
                session.commit()

        return jsonify({"message": "Forløb created successfully", "uid": forloeb.ForløbID}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloeb(forloeb_id):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=forloeb_id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        result = {
            "ForløbID": forloeb.ForløbID,
            "name": forloeb.name,
            "startdate": forloeb.startdate.isoformat(),
            "enddate": forloeb.enddate.isoformat(),
            "admin": forloeb.admin,
            "usermail": forloeb.usermail,
            "userdq": forloeb.userdq
        }
        return jsonify(result), 200
    except Exception as e:
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


def get_forloeb_by_email(mail):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(usermail=mail).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        result = {
            "ForløbID": forloeb.ForløbID,
            "name": forloeb.name,
            "startdate": forloeb.startdate.isoformat(),
            "enddate": forloeb.enddate.isoformat(),
            "admin": forloeb.admin,
            "usermail": forloeb.usermail,
            "userdq": forloeb.userdq
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def get_forloeb_by_admin(admin_name):
    session = db_client.get_session()
    try:
        forloeb_list = session.query(Forløb).filter_by(admin=admin_name).all()
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


def download_forloeb():
    try:
        # Get the forløb ID from the query parameters
        forloeb_id = int(request.args.get('id'))

        # Fetch forløb and opgaver data
        forloeb = get_forloeb(forloeb_id)[0].json  # Extract JSON data from response
        opgaver = get_opgave_by_forloeb_id(forloeb_id).json
        logger.info(f"Fetched forløb: {forloeb}, opgaver: {opgaver}")

        # Initialize FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add Forløb details
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(0, 10, forloeb['name'], ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Onboardingforløb med start d. {forloeb['startdate']}", ln=True)
        pdf.ln(10)

        # Add a line separator
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

        # Add Opgaver details
        for opgave in opgaver:
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(0, 10, opgave['title'], ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Startdato: {opgave['startdato']}", ln=True)
            pdf.multi_cell(0, 10, opgave['beskrivelse'])
            pdf.cell(0, 10, f"Ansvarlig: {opgave['ansvarlig']} ({opgave['ansvarligEmail']})", ln=True)
            pdf.ln(10)

        # Generate PDF content
        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={forloeb["name"]}.pdf'
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_forloeb(id):
    data = request.json
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        forloeb.name = data.get('name', forloeb.name)
        forloeb.startdate = data.get('startdate', forloeb.startdate)
        forloeb.enddate = data.get('enddate', forloeb.enddate)
        forloeb.admin = data.get('admin', forloeb.admin)
        forloeb.usermail = data.get('usermail', forloeb.usermail)
        forloeb.userdq = data.get('userdq', forloeb.userdq)

        session.commit()
        return jsonify({"message": "Forløb updated successfully", "uid": forloeb.ForløbID}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def complete_forloeb(id):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        forloeb.enddate = datetime.now()
        session.commit()
        return jsonify({"message": "Forløb completed successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


def delete_forloeb(id):
    session = db_client.get_session()
    try:
        forloeb = session.query(Forløb).filter_by(ForløbID=id).first()
        if not forloeb:
            return jsonify({"error": "Forløb not found"}), 404

        session.delete(forloeb)
        session.commit()
        return jsonify({"message": "Forløb deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

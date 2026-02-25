from datetime import datetime
from fpdf import FPDF


def create_pdf(forloeb_id):
    from controllers.opgave_controller import get_opgave_by_forloeb_id
    from controllers.forloeb_controller import get_forloeb

    # Fetch forløb and opgaver data
    forloeb_response = get_forloeb(forloeb_id)
    forloeb = forloeb_response[0].get_json() if isinstance(forloeb_response, tuple) else forloeb_response.get_json()
    opgaver_response = get_opgave_by_forloeb_id(forloeb_id)
    opgaver = opgaver_response[0].get_json() if isinstance(opgaver_response, tuple) else opgaver_response.get_json()
    if "error" not in opgaver:
        opgaver = sorted(opgaver, key=lambda x: x["startdato"])

    # Initialize FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # Add Forløb details
    pdf.set_font("Arial", style="B", size=18)
    pdf.cell(0, 10, forloeb['name'], ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Onboardingforløb med start d. {datetime.strptime(forloeb['startdate'], '%Y-%m-%dT%H:%M:%S').strftime('%d-%m-%Y')}", ln=True)
    pdf.ln(5)

    # Add a line separator
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Add Opgaver details
    if "error" not in opgaver:
        for opgave in opgaver:
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", style="B", size=13)
            pdf.cell(0, 10, opgave['title'], ln=True)

            pdf.set_text_color(100, 100, 100)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 3, f"Startdato: {datetime.strptime(opgave['startdato'], '%Y-%m-%dT%H:%M:%S').strftime('%d-%m-%Y')}", ln=True)

            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 20, opgave['beskrivelse'])

            if opgave.get('resourcer') and len(opgave['resourcer']) > 0:
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 10, "Ressourcer: ", ln=True)
                resources_text = ", ".join([f"{resource['name']} ({resource['url']})" for resource in opgave.get('resourcer', [])])
                pdf.set_text_color(100, 100, 255)
                pdf.multi_cell(0, 3, resources_text)

            if opgave['ansvarlig']:
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 10, f"Ansvarlig: {opgave['ansvarlig']} ({opgave.get('ansvarligEmail', '')})", ln=True)
            pdf.ln(10)

    return pdf.output(dest='S').encode('latin1')

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import base64

def create_pdf(summary, environment, equipment_counts, tower_load):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, height - 50, "Technical Proposal Analysis Report")

    c.setFont("Helvetica", 12)
    y = height - 100
    c.drawString(50, y, "Structural Technical Summary:")
    y -= 20
    for key, val in summary.items():
        c.drawString(60, y, f"{key}: {val}")
        y -= 20

    y -= 10
    c.drawString(50, y, "Aerial / Environmental Situation:")
    y -= 20
    for key, val in environment.items():
        c.drawString(60, y, f"{key}: {val}")
        y -= 20

    y -= 10
    c.drawString(50, y, "Equipment Comparison:")
    y -= 20
    for category, row in equipment_counts.iterrows():
        c.drawString(60, y, f"{category}: Before={row['Before']} After={row['After']}")
        y -= 20

    y -= 10
    c.drawString(50, y, "Tower Load Comparison:")
    y -= 20
    for condition, row in tower_load.iterrows():
        c.drawString(60, y, f"{condition}: {row['Load (kg)']} kg")
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

def download_pdf(buffer):
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="analysis_report.pdf">📥 Download Analysis Report (PDF)</a>'
    return href

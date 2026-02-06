from reportlab.pdfgen import canvas
from utils.pdf_builder import build_variance_pdf
import os
import uuid


def generate_variance_pdf_file(kpi_summary, variance, ai_insight=None):
    filename = f"variance_report_{uuid.uuid4().hex}.pdf"
    path = os.path.join("temp", filename)

    os.makedirs("temp", exist_ok=True)

    c = canvas.Canvas(path)
    build_variance_pdf(c, kpi_summary, variance, ai_insight)
    c.showPage()
    c.save()

    return path

from io import BytesIO
from reportlab.pdfgen import canvas
from utils.pdf_builder import build_variance_pdf
from reportlab.lib.pagesizes import letter  # ← add this

def generate_variance_pdf_stream(kpi_summary, variance, ai_insight=""):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    build_variance_pdf(c, kpi_summary, variance, ai_insight)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

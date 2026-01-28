from reportlab.pdfgen import canvas

def build_variance_pdf(canvas_obj, kpi_summary, variance, ai_insight=None):
    y = 750

    canvas_obj.setFont("Helvetica", 10)

    canvas_obj.drawString(40, y, "KPI SUMMARY")
    y -= 20

    for k in kpi_summary:
        label = k["label"] if isinstance(k, dict) else k.label
        value = k["value"] if isinstance(k, dict) else k.value
        canvas_obj.drawString(40, y, f"{label}: {value}")

        y -= 20

    y -= 20
    canvas_obj.drawString(40, y, "VARIANCE")
    y -= 20

    for v in variance:
        canvas_obj.drawString(40, y, str(v))
        y -= 15

    if ai_insight:
        y -= 20
        canvas_obj.drawString(40, y, "AI INSIGHTS")
        y -= 20
        for line in ai_insight.split("\n"):
            canvas_obj.drawString(40, y, line)
            y -= 15

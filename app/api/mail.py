from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from app.core.database import get_connection

router = APIRouter(tags=["Mail Content"])


class MailRequest(BaseModel):
    session_id: str


@router.post("/content")
def generate_mail_content(request: MailRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT result_json FROM analysis_results WHERE session_id = ?",
        (request.session_id,),
    )
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=400, detail="Analysis not found")

    analysis_data = json.loads(row["result_json"])

    subject = "KPI Variance & Forecast Report"

    body_html = f"""
    <h2>KPI Performance Summary</h2>
    <pre>{json.dumps(analysis_data, indent=2)}</pre>
    """

    return {
        "subject": subject,
        "body_text": json.dumps(analysis_data, indent=2),
        "body_html": body_html,
    }

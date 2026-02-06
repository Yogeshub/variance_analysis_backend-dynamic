from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.database import get_connection
from app.services.export_service import generate_pdf, generate_docx
import json
from pydantic import BaseModel

router = APIRouter(tags=["Export"])


class AIInsightsRequest(BaseModel):
    session_id: str


# @router.get("/pdf/{session_id}")
# def export_pdf(session_id: str):
#
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT result_json FROM analysis_results WHERE session_id = ?",
#                    (session_id,))
#     row = cursor.fetchone()
#
#     if not row:
#         raise HTTPException(status_code=400, detail="No analysis found")
#
#     data = json.loads(row["result_json"])
#     file_path = generate_pdf(session_id, data)
#
#     conn.close()
#
#     return FileResponse(file_path, media_type="application/pdf")
#
#
# @router.get("/docx/{session_id}")
# def export_docx(session_id: str):
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT result_json FROM analysis_results WHERE session_id = ?",
#                    (session_id,))
#     row = cursor.fetchone()
#
#     if not row:
#         raise HTTPException(status_code=400, detail="No analysis found")
#
#     data = json.loads(row["result_json"])
#     file_path = generate_docx(session_id, data)
#
#     conn.close()
#
#     return FileResponse(file_path, media_type="application/docx")


@router.post("/export/pdf")
def export_pdf(request: AIInsightsRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT result_json, ai_insights_json
        FROM analysis_results
        WHERE session_id=?
    """,
        (request.session_id,),
    )
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=400, detail="Analysis not found")

    analysis_data = json.loads(row["result_json"])
    ai_data = json.loads(row["ai_insights_json"]) if row["ai_insights_json"] else {}

    file_path = f"temp/report_{request.session_id}.pdf"

    # from app.services.pdf_service import generate_pdf
    generate_pdf(file_path, analysis_data, ai_data)

    return {"file_path": file_path}


@router.post("/export/docx")
def export_docx(request: AIInsightsRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT result_json, ai_insights_json
        FROM analysis_results
        WHERE session_id=?
    """,
        (request.session_id,),
    )
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=400, detail="Analysis not found")

    analysis_data = json.loads(row["result_json"])
    ai_data = json.loads(row["ai_insights_json"]) if row["ai_insights_json"] else {}

    file_path = f"temp/report_{request.session_id}.docx"

    # from app.services.docx_service import generate_docx
    generate_docx(file_path, analysis_data, ai_data)

    return {"file_path": file_path}

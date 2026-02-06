from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.database import get_connection
from app.services.ai_service import generate_ai_insight
import json

router = APIRouter(tags=["AI - Insights"])


class AIInsightsRequest(BaseModel):
    session_id: str
    custom_prompt: str | None = None


#
# @router.post("/ai-insights")
# def generate_insights(request: AIInsightRequest):
#
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT result_json FROM analysis_results WHERE session_id = ?",
#                    (request.session_id,))
#     row = cursor.fetchone()
#
#     if not row:
#         raise HTTPException(status_code=400, detail="No analysis results found")
#
#     analysis_data = json.loads(row["result_json"])
#
#     insight = generate_ai_insight(analysis_data)
#
#     conn.close()
#
#     return {
#         "session_id": request.session_id,
#         "ai_insights": insight
#     }



@router.post("/ai-insights")
async def generate_ai_insights(request: AIInsightsRequest):

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
        conn.close()
        raise HTTPException(status_code=400, detail="Analysis not found")

    # If cached → return immediately
    if row["ai_insights_json"]:
        conn.close()
        return json.loads(row["ai_insights_json"])

    analysis_data = json.loads(row["result_json"])

    from app.services.ai_service import generate_ai_insight

    # ✅ AWAIT the async function
    ai_response = await generate_ai_insight(
        analysis_data=analysis_data, custom_prompt=request.custom_prompt
    )

    # Cache it
    cursor.execute(
        """
        UPDATE analysis_results
        SET ai_insights_json=?
        WHERE session_id=?
    """,
        (json.dumps(ai_response), request.session_id),
    )

    conn.commit()
    conn.close()

    return ai_response

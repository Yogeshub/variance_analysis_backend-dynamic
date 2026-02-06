# # # app/api/chat.py
# #
# # from fastapi import APIRouter
# # from fastapi.responses import StreamingResponse
# # from pydantic import BaseModel
# # from typing import Optional, Dict
# # import uuid
# # import json
# # import os
# # import httpx
# #
# # from app.utils.session_store import chat_sessions
# #
# # router = APIRouter()
# #
# # # =====================
# # # Models
# # # =====================
# #
# # class ChatStreamRequest(BaseModel):
# #     session_id: Optional[str] = None
# #     message: Optional[str] = None
# #     auto_prompt: Optional[str] = None
# #     context: Dict
# #
# #
# # # =====================
# # # Constants
# # # =====================
# #
# # AUTO_PROMPTS = {
# #     "explain_variance": "Explain the major variances and their business impact.",
# #     "key_risks": "Identify key financial and operational risks from the data.",
# #     "recommendations": "Provide actionable recommendations based on KPIs and variance.",
# #     "executive_summary": "Create an executive-level summary of overall performance."
# # }
# #
# # GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# # GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# #
# #
# # # =====================
# # # Routes
# # # =====================
# #
# # @router.post("/chat/stream")
# # async def stream_chat(payload: ChatStreamRequest):
# #     """
# #     Stream AI assistant responses for Ask AI chat.
# #     Supports session memory, context, and streaming responses.
# #     """
# #
# #     # 1️⃣ Session handling
# #     session_id = payload.session_id or str(uuid.uuid4())
# #     if session_id not in chat_sessions:
# #         chat_sessions[session_id] = []
# #
# #     history = chat_sessions[session_id]
# #
# #     # 2️⃣ Resolve user message
# #     user_message = payload.message
# #     if payload.auto_prompt:
# #         user_message = AUTO_PROMPTS.get(payload.auto_prompt)
# #
# #     if not user_message:
# #         return {"error": "Message or auto_prompt required"}
# #
# #     # 3️⃣ System prompt (only once per session)
# #     context_data = payload.context or {}
# #
# #     system_prompt = f"""
# # You are a senior financial analyst AI.
# #
# # STRICT RULES:
# # - Use ONLY the provided data
# # - No hallucination
# # - Be concise and analytical
# #
# # CONTEXT DATA:
# # {json.dumps(context_data, indent=2)}
# # """
# #
# #     if not any(m["role"] == "system" for m in history):
# #         history.append({"role": "system", "content": system_prompt})
# #
# #     # 4️⃣ Append user message
# #     history.append({"role": "user", "content": user_message})
# #
# #     # 5️⃣ Groq payload
# #     groq_payload = {
# #         "model": "llama-3.3-70b-versatile",
# #         "stream": True,
# #         "messages": history,
# #     }
# #
# #     headers = {
# #         "Authorization": f"Bearer {GROQ_API_KEY}",
# #         "Content-Type": "application/json",
# #     }
# #
# #     # 6️⃣ Streaming generator
# #     async def event_generator():
# #         assistant_reply = ""
# #
# #         async with httpx.AsyncClient(verify=False, timeout=120) as client:
# #             async with client.stream(
# #                 "POST",
# #                 GROQ_URL,
# #                 headers=headers,
# #                 json=groq_payload,
# #             ) as response:
# #
# #                 async for line in response.aiter_lines():
# #                     if not line or not line.startswith("data:"):
# #                         continue
# #
# #                     data = line.replace("data:", "").strip()
# #                     if data == "[DONE]":
# #                         break
# #
# #                     try:
# #                         parsed = json.loads(data)
# #                         delta = (
# #                             parsed.get("choices", [{}])[0]
# #                             .get("delta", {})
# #                             .get("content")
# #                         )
# #
# #                         if delta:
# #                             assistant_reply += delta
# #                             yield delta
# #
# #                     except Exception:
# #                         continue
# #
# #         # 7️⃣ Save assistant reply
# #         history.append({"role": "assistant", "content": assistant_reply})
# #
# #     # 8️⃣ Return stream
# #     return StreamingResponse(
# #         event_generator(),
# #         media_type="text/plain",
# #         headers={"X-Session-ID": session_id},
# #     )
# #
# #
# # @router.post("/chat/reset/{session_id}")
# # def reset_chat(session_id: str):
# #     chat_sessions.pop(session_id, None)
# #     return {"status": "reset", "session_id": session_id}
#
#
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from app.core.database import get_connection
# from app.services.chat_service import generate_chat_reply
# import json
#
# router = APIRouter(tags=["Chat"])
#
#
# class ChatRequest(BaseModel):
#     session_id: str
#     message: str
#
#
# @router.post("/message")
# def chat_message(request: ChatRequest):
#
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     # Save user message
#     cursor.execute("""
#         INSERT INTO chat_history (session_id, role, message)
#         VALUES (?, ?, ?)
#     """, (request.session_id, "user", request.message))
#
#     conn.commit()
#
#     reply = generate_chat_reply(request.session_id)
#
#     # Save assistant reply
#     cursor.execute("""
#         INSERT INTO chat_history (session_id, role, message)
#         VALUES (?, ?, ?)
#     """, (request.session_id, "assistant", reply))
#
#     conn.commit()
#     conn.close()
#
#     return {"reply": reply}


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from app.core.database import get_connection
from app.services.chat_service import generate_chat_response

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


# @router.post("/message")
# async def chat_message(request: ChatRequest):
#
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     # Load analysis context
#     cursor.execute("SELECT result_json FROM analysis_results WHERE session_id = ?",
#                    (request.session_id,))
#     row = cursor.fetchone()
#
#     if not row:
#         raise HTTPException(status_code=400, detail="Analysis not found for this session")
#
#     analysis_data = json.loads(row["result_json"])
#
#     # Save user message
#     cursor.execute("INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
#                    (request.session_id, "user", request.message))
#
#     response_text = generate_chat_response(request.message, analysis_data)
#
#     # Save assistant reply
#     cursor.execute("INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
#                    (request.session_id, "assistant", response_text))
#
#     conn.commit()
#     conn.close()
#
#     return {"reply": response_text}


@router.post("/message")
async def chat_message(request: ChatRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT result_json FROM analysis_results WHERE session_id = ?",
        (request.session_id,),
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Analysis not found for this session"
        )

    analysis_data = json.loads(row["result_json"])

    # Save user message
    cursor.execute(
        "INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
        (request.session_id, "user", request.message),
    )

    # ✅ Await the async AI function
    response_text = await generate_chat_response(request.message, analysis_data)

    # Save assistant reply
    cursor.execute(
        "INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
        (request.session_id, "assistant", response_text),
    )

    conn.commit()
    conn.close()

    return {"reply": response_text}

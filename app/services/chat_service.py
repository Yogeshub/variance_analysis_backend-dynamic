# # import uuid
# # import json
# # import httpx
# # from fastapi.responses import StreamingResponse
# # from app.core.config import settings
# # from app.utils.session_store import chat_sessions
# #
# # async def stream_chat(payload):
# #
# #     session_id = payload.session_id or str(uuid.uuid4())
# #     if session_id not in chat_sessions:
# #         chat_sessions[session_id] = []
# #
# #     history = chat_sessions[session_id]
# #
# #     history.append({"role": "user", "content": payload.message})
# #
# #     headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
# #
# #     async def event_generator():
# #         assistant_reply = ""
# #
# #         async with httpx.AsyncClient(timeout=120) as client:
# #             async with client.stream(
# #                 "POST",
# #                 settings.GROQ_URL,
# #                 headers=headers,
# #                 json={
# #                     "model": "llama-3.3-70b-versatile",
# #                     "stream": True,
# #                     "messages": history
# #                 }
# #             ) as response:
# #
# #                 async for line in response.aiter_lines():
# #                     if not line.startswith("data:"):
# #                         continue
# #
# #                     data = line.replace("data:", "").strip()
# #                     if data == "[DONE]":
# #                         break
# #
# #                     parsed = json.loads(data)
# #                     delta = parsed["choices"][0]["delta"].get("content")
# #
# #                     if delta:
# #                         assistant_reply += delta
# #                         yield delta
# #
# #         history.append({"role": "assistant", "content": assistant_reply})
# #
# #     return StreamingResponse(event_generator(), media_type="text/plain")
# import os
import httpx
from app.core.database import get_connection

#
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GROQ_URL = os.getenv("GROQ_URL")
#
# async def generate_chat_reply(session_id: str):
#     if not GROQ_API_KEY or not GROQ_URL:
#         raise RuntimeError("GROQ_API_KEY or GROQ_URL not set")
#
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#
#     # Fetch chat history
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     cursor.execute("""
#         SELECT role, message
#         FROM chat_history
#         WHERE session_id = ?
#         ORDER BY created_at ASC
#     """, (session_id,))
#
#     rows = cursor.fetchall()
#     conn.close()
#
#     messages = [
#         {"role": row["role"], "content": row["message"]}
#         for row in rows
#     ]
#
#     async with httpx.AsyncClient(timeout=60) as client:
#         response = await client.post(
#             GROQ_URL,
#             json={
#                 "model": "llama-3.3-70b-versatile",
#                 "messages": messages,
#                 "temperature": 0.4
#             },
#             headers=headers
#         )
#
#         response.raise_for_status()
#         result = response.json()
#
#         return result["choices"][0]["message"]["content"]
#
#

import httpx
import os
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = os.getenv("GROQ_URL")

# async def generate_chat_response(user_message, analysis_data):
#     if not GROQ_API_KEY or not GROQ_URL:
#         raise RuntimeError("GROQ_API_KEY or GROQ_URL not set")
#
#     headers = {
#             "Authorization": f"Bearer {GROQ_API_KEY}",
#             "Content-Type": "application/json"
#     }
#
#
#     prompt = f"""
#     You are a financial analytics assistant.
#
#     Use ONLY the following KPI analysis context:
#
#     {json.dumps(analysis_data, indent=2)}
#
#     User Question:
#     {user_message}
#     """
#
#
#     async with httpx.AsyncClient(timeout=60) as client:
#             completion = await client.post(
#                     GROQ_URL,
#                     json={
#                         "model": "llama-3.3-70b-versatile",
#                         "messages": [{"role": "user", "content": prompt}],
#                         "temperature": 0.4
#                     },
#                     headers=headers
#             )
#
#
#     return completion.choices[0].message.content


async def generate_chat_response(user_message, analysis_data):
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_URL = os.getenv("GROQ_URL")

    if not GROQ_API_KEY or not GROQ_URL:
        raise RuntimeError("GROQ_API_KEY or GROQ_URL not set")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = f"""
You are a financial analytics assistant.

Use ONLY the following KPI analysis context:

{json.dumps(analysis_data, indent=2)}

User Question:
{user_message}
"""

    async with httpx.AsyncClient(timeout=60) as client:
        completion = await client.post(
            GROQ_URL,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
            },
            headers=headers,
        )

    completion.raise_for_status()

    response_json = completion.json()
    content = response_json["choices"][0]["message"]["content"]

    return content

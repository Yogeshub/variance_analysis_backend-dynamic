import uuid
import json
import httpx
from fastapi.responses import StreamingResponse
from app.core.config import settings
from app.utils.session_store import chat_sessions

async def stream_chat(payload):

    session_id = payload.session_id or str(uuid.uuid4())
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    history = chat_sessions[session_id]

    history.append({"role": "user", "content": payload.message})

    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    async def event_generator():
        assistant_reply = ""

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                settings.GROQ_URL,
                headers=headers,
                json={
                    "model": "llama-3.3-70b-versatile",
                    "stream": True,
                    "messages": history
                }
            ) as response:

                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue

                    data = line.replace("data:", "").strip()
                    if data == "[DONE]":
                        break

                    parsed = json.loads(data)
                    delta = parsed["choices"][0]["delta"].get("content")

                    if delta:
                        assistant_reply += delta
                        yield delta

        history.append({"role": "assistant", "content": assistant_reply})

    return StreamingResponse(event_generator(), media_type="text/plain")

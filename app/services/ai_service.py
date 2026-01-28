import httpx
from app.core.config import settings
import json

async def generate_ai_insight(payload):
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    prompt = f"""
    Analyze the KPI data and provide insights:
    {json.dumps(payload, indent=2)}
    """

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(
            settings.GROQ_URL,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}]
            },
            headers=headers
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]

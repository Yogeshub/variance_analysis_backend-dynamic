import httpx
import os, json

# from app.core.config import settings

#
# async def generate_ai_insight(payload):
#     headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
#
#     prompt = f"""
#     Analyze the KPI data and provide insights:
#     {json.dumps(payload, indent=2)}
#     """
#
#     async with httpx.AsyncClient(timeout=60) as client:
#         res = await client.post(
#             settings.GROQ_URL,
#             json={
#                 "model": "llama-3.3-70b-versatile",
#                 "messages": [{"role": "user", "content": prompt}]
#             },
#             headers=headers
#         )
#         res.raise_for_status()
#         return res.json()["choices"][0]["message"]["content"]


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = os.getenv("GROQ_URL")
#
# async def generate_ai_insight(analysis_data):
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#
#     prompt = f"""
#     You are a senior banking analytics expert.
#
#     Return response STRICTLY in JSON format:
#
#     {{
#       "executive_summary": "...",
#       "key_risks": ["...", "..."],
#       "opportunities": ["...", "..."],
#       "forecast_outlook": "...",
#       "strategic_recommendations": ["...", "..."]
#     }}
#
#     KPI Data:
#     {analysis_data}
#     """
#
#     async with httpx.AsyncClient(timeout=60) as client:
#         response = await client.post(
#             GROQ_URL,
#             json={
#                 "model": "llama-3.3-70b-versatile",
#                 "messages": [
#                     {"role": "user", "content": prompt}
#                 ]
#             },
#             headers=headers
#         )
#
#         # response.raise_for_status()
#         # result = response.json()
#         #
#         # return result["choices"][0]["message"]["content"]
#         content = response.choices[0].message.content
#         structured = json.loads(content)
#         return structured


async def generate_ai_insight(analysis_data, custom_prompt=None):
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_URL = os.getenv("GROQ_URL")

    if not GROQ_URL:
        raise RuntimeError("GROQ_URL not set")

    prompt = f"""
    You are a senior financial analytics expert.

    Return STRICT JSON only in this format:

    {{
      "executive_summary": "...",
      "key_risks": ["...", "..."],
      "opportunities": ["...", "..."],
      "forecast_outlook": "...",
      "strategic_recommendations": ["...", "..."]
    }}

    User Prompt: {custom_prompt or "Provide full performance analysis"}
    KPI Data:
    {json.dumps(analysis_data, indent=2)}
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        completion = await client.post(
            GROQ_URL,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            headers=headers,
        )

    completion.raise_for_status()

    response_json = completion.json()
    content = response_json["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "executive_summary": content,
            "key_risks": [],
            "opportunities": [],
            "forecast_outlook": "",
            "strategic_recommendations": [],
        }

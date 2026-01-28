import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    EMAIL_TO = os.getenv("EMAIL_TO")
    EMAIL_CC = os.getenv("EMAIL_CC")
    EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "KPI Variance Report")

    ALLOWED_DOMAINS = ["banking"]

settings = Settings()

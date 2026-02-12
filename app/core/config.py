import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Variance Analysis Enterprise Engine"
    VERSION: str = "1.0.0"

    # File Controls

    MAX_FILE_SIZE_MB: int = 10
    MAX_ROWS: int = 100_000

    # Database
    DATABASE_URL: str = "sqlite:///./kpi_app.db"

    # AI
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


settings = Settings()

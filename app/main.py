# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.core.database import engine
# from app.models import db_models
# from app.api import health_api
# from app.core.config import settings
# from app.api import upload_api
#
# # Create DB tables
# db_models.Base.metadata.create_all(bind=engine)
#
# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.VERSION
# )
#
# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Register routers
# app.include_router(health_api.router, prefix="/api")
# app.include_router(upload_api.router, prefix="/api")


from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.database import init_db
from app.api import session, dataset, ai, analyze, chat, export, admin, mail, prompts
import os, httpx

load_dotenv()
_original_client = httpx.Client
_original_async_client = httpx.AsyncClient


def patched_client(*args, **kwargs):
    kwargs["verify"] = False
    return _original_client(*args, **kwargs)


def patched_async_client(*args, **kwargs):
    kwargs["verify"] = False
    return _original_async_client(*args, **kwargs)


httpx.Client = patched_client
httpx.AsyncClient = patched_async_client

APP_NAME = os.getenv("APP_NAME", "Enterprise Variance Analysis API")

app = FastAPI(title=APP_NAME)


@app.on_event("startup")
def startup_event():
    init_db()


app.include_router(session.router, prefix="/session")
app.include_router(dataset.router, prefix="/dataset")
app.include_router(analyze.router, prefix="/analysis")
app.include_router(ai.router, prefix="/analysis")
app.include_router(chat.router, prefix="/chat")
app.include_router(export.router, prefix="/export")
app.include_router(mail.router, prefix="/mail")
app.include_router(prompts.router, prefix="/prompts")
app.include_router(admin.router, prefix="/admin")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analyze

app = FastAPI(title="Enterprise Variance Analytics Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/analyze", tags=["Analyze"])

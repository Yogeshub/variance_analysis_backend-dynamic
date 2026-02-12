from typing import List, Optional
from pydantic import BaseModel


class AnalysisRunRequest(BaseModel):
    session_id: str
    domain: str
    selected_kpis: List[str]
    forecast_periods: int = 6


class AnalysisRequest(BaseModel):
    session_id: str
    selected_kpis: List[str]
    forecast_periods: int = 6
    selected_subdomains: Optional[List[str]] = None

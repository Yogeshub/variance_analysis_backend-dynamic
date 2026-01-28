from fastapi import APIRouter, UploadFile, File, Form
from app.services.file_service import parse_file, validate_domain
from app.services.kpi_service import discover_kpis
from app.services.variance_service import compute_variance
from app.services.forecast_service import forecast_next_period
import json

router = APIRouter()

@router.post("/")
async def analyze(
    file: UploadFile = File(...),
    domain: str = Form(...)
):
    content = await file.read()
    df = parse_file(content, file.filename)

    config = validate_domain(df, domain)

    kpi = discover_kpis(df, config["date_column"])
    variance = compute_variance(kpi)
    forecast = forecast_next_period(kpi)

    return {
        "kpi": kpi.to_dict(orient="records"),
        "variance": variance.to_dict(orient="records"),
        "forecast": forecast
    }

from fastapi import APIRouter
from app.services.forecasting_service import forecast_metric

router = APIRouter()


@router.post("/forecast")
async def forecast(data: dict):

    df = data["kpi_df"]
    metric = data["metric"]

    return forecast_metric(df, metric)

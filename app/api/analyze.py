# from fastapi import APIRouter, UploadFile, File, Form,HTTPException
# # from app.services.file_service import parse_file, validate_domain
# # from app.services.kpi_service import discover_kpis
# # from app.services.variance_service import compute_variance
# # from app.services.forecast_service import forecast_next_period
# # import json
# from app.services.forecast_service import ForecastService
# from app.utils.date_utils import detect_date_column
# from app.models.analysis_models import AnalysisRunRequest
# from app.services.dataset_service import DatasetService
#
#
#
#
# router = APIRouter()
#
# # @router.post("/")
# # async def analyze(
# #     file: UploadFile = File(...),
# #     domain: str = Form(...)
# # ):
# #     content = await file.read()
# #     df = parse_file(content, file.filename)
# #
# #     config = validate_domain(df, domain)
# #
# #     kpi = discover_kpis(df, config["date_column"])
# #     variance = compute_variance(kpi)
# #     forecast = forecast_next_period(kpi)
# #
# #
# #     return {
# #         "kpi": kpi.to_dict(orient="records"),
# #         "variance": variance.to_dict(orient="records"),
# #         "forecast": forecast
# #     }
#
# @router.post("/run")
# def run_analysis(request: AnalysisRunRequest):
#
#     df = DatasetService.load_dataset(request.session_id)
#
#     if df is None:
#         raise HTTPException(status_code=400, detail="Invalid session or dataset not uploaded")
#
#     possible_dates = [col for col in df.columns if "date" in col.lower()]
#
#     if not possible_dates:
#         raise HTTPException(status_code=400, detail="No date column found")
#
#     date_column = possible_dates[0]
#
#     variance_results = VarianceService.calculate_variance(
#         df,
#         request.selected_kpis
#     )
#
#     forecast_results = ForecastService.forecast_multiple(
#         df=df,
#         date_column=date_column,
#         kpis=request.selected_kpis,
#         periods=request.forecast_periods
#     )
#
#     return {
#         "variance": variance_results,
#         "forecast": forecast_results
#     }


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
from prophet import Prophet
from app.core.database import get_connection
from app.services.analysis_service import make_json_serializable
from typing import List, Optional

router = APIRouter(tags=["Analyze"])


class AnalysisRequest(BaseModel):
    session_id: str
    selected_kpis: List[str]
    forecast_periods: int = 6
    selected_subdomains: Optional[List[str]] = None


def forecast_kpi(df, date_column, kpi, periods):
    model_df = df[[date_column, kpi]].dropna()

    if model_df.empty:
        return []

    model_df.columns = ["ds", "y"]

    model = Prophet()
    model.fit(model_df)

    future = model.make_future_dataframe(periods=periods, freq="M")
    forecast = model.predict(future)

    # return forecast[["ds", "yhat"]].tail(periods).to_dict(orient="records")
    future_df = forecast[["ds", "yhat"]].tail(periods)

    return {
        "dates": future_df["ds"].astype(str).tolist(),
        "values": future_df["yhat"].tolist(),
    }


@router.post("/run")
def run_analysis(request: AnalysisRequest):

    if not request.selected_kpis:
        raise HTTPException(status_code=400, detail="No KPIs selected")

    if request.forecast_periods < 1 or request.forecast_periods > 24:
        raise HTTPException(
            status_code=400, detail="Forecast periods must be between 1 and 24"
        )

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch dataset + metadata
    cursor.execute(
        """
        SELECT dataset_json, date_column, subdomain_column
        FROM datasets
        WHERE session_id = ?
    """,
        (request.session_id,),
    )

    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=400, detail="Invalid session or dataset not uploaded"
        )

    df = pd.read_json(row["dataset_json"])
    date_column = row["date_column"]
    subdomain_column = row["subdomain_column"]

    if date_column not in df.columns:
        raise HTTPException(
            status_code=400, detail="Stored date column not found in dataset"
        )

    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(date_column)

    # ✅ SUBDOMAIN FILTERING LOGIC
    if request.selected_subdomains:

        if not subdomain_column:
            raise HTTPException(
                status_code=400, detail="No subdomain column available in dataset"
            )

        if subdomain_column not in df.columns:
            raise HTTPException(
                status_code=400, detail="Subdomain column not found in dataset"
            )

        df = df[df[subdomain_column].isin(request.selected_subdomains)]

        if df.empty:
            raise HTTPException(
                status_code=400, detail="No data found for selected subdomains"
            )

    results = {}

    for kpi in request.selected_kpis:

        if kpi not in df.columns:
            continue

        if not pd.api.types.is_numeric_dtype(df[kpi]):
            continue

        if df[kpi].isnull().all():
            raise HTTPException(
                status_code=400, detail=f"KPI {kpi} contains only null values"
            )

        total = float(df[kpi].sum())
        mean = float(df[kpi].mean())
        std = float(df[kpi].std())

        variance = df[kpi].diff().iloc[-1] if len(df) > 1 else 0

        forecast = forecast_kpi(df, date_column, kpi, request.forecast_periods)

        results[kpi] = {
            "summary": {"total": total, "mean": mean, "std": std},
            "variance_latest": float(variance),
            "time_series": {
                "dates": df[date_column].astype(str).tolist(),
                "values": df[kpi].tolist(),
            },
            "forecast": forecast,
        }

    if not results:
        raise HTTPException(status_code=400, detail="No valid KPI data found")

    cursor.execute(
        """
        INSERT OR REPLACE INTO analysis_results (session_id, result_json)
        VALUES (?, ?)
    """,
        (request.session_id, json.dumps(results, default=make_json_serializable)),
    )

    conn.commit()
    conn.close()

    return {
        "message": "Analysis completed successfully",
        "session_id": request.session_id,
        "kpi_results": results,
    }

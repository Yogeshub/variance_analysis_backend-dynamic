import pandas as pd
from prophet import Prophet


class ForecastService:

    @staticmethod
    def forecast_single(df: pd.DataFrame, date_column: str, kpi: str, periods: int = 6):
        try:
            temp_df = df[[date_column, kpi]].copy()
            temp_df = temp_df.rename(columns={date_column: "ds", kpi: "y"})
            temp_df["ds"] = pd.to_datetime(temp_df["ds"], errors="coerce")

            temp_df = temp_df.dropna()
            temp_df = temp_df.sort_values("ds")

            if temp_df.empty or len(temp_df) < 3:
                return {"error": f"Not enough data to forecast {kpi}"}

            model = Prophet()
            model.fit(temp_df)

            future = model.make_future_dataframe(periods=periods, freq="M")
            forecast = model.predict(future)

            result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)

            return result.to_dict(orient="records")

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def forecast_multiple(
        df: pd.DataFrame, date_column: str, kpis: list, periods: int = 6
    ):
        results = {}

        for kpi in kpis:
            results[kpi] = ForecastService.forecast_single(
                df, date_column, kpi, periods
            )

        return results

from sklearn.linear_model import LinearRegression
import numpy as np

def forecast_next_period(kpi_df):
    forecasts = {}

    if len(kpi_df) < 2:
        return {}

    for col in kpi_df.columns:
        if col == "ReportingMonth":
            continue

        y = kpi_df[col].values
        X = np.arange(len(y)).reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        next_pred = model.predict([[len(y)]])[0]
        forecasts[col] = round(float(next_pred), 2)

    return forecasts

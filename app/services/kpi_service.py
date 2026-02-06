import pandas as pd


def discover_kpis(df: pd.DataFrame):
    valid_kpis = []
    invalid_kpis = []

    for col in df.columns:
        series = df[col]

        # Skip obvious dimension columns
        if series.dtype == "object":
            invalid_kpis.append({"column": col, "reason": "Non-numeric column"})
            continue

        # Convert numeric safely
        numeric_series = pd.to_numeric(series, errors="coerce")

        null_ratio = numeric_series.isna().mean()

        if null_ratio > 0.3:
            invalid_kpis.append({"column": col, "reason": "Too many missing values"})
            continue

        if numeric_series.nunique() <= 1:
            invalid_kpis.append({"column": col, "reason": "No variance in data"})
            continue

        # valid_kpis.append({
        #     "column": col,
        #     "sample_mean": round(numeric_series.mean(), 2),
        #     "sample_std": round(numeric_series.std(), 2)
        # })
        valid_kpis.append(
            {
                "column": col,
            }
        )

    return valid_kpis, invalid_kpis

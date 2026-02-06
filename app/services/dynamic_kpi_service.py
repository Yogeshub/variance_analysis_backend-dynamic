import pandas as pd


def discover_numeric_kpis(df, date_column):

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df["Period"] = df[date_column].dt.to_period("M")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    grouped = df.groupby("Period")[numeric_cols].agg(["sum", "mean"]).reset_index()

    grouped.columns = [
        f"{col[0]}_{col[1]}" if col[1] else col[0] for col in grouped.columns
    ]

    grouped["Period"] = grouped["Period"].astype(str)

    return grouped

import pandas as pd


def detect_date_column(df: pd.DataFrame):

    possible = ["date", "month", "business_date", "txn_date"]

    for col in df.columns:
        if col.lower() in possible:
            return col

    # fallback: check datetime type
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            return col
        except:
            continue

    raise ValueError("No valid date column detected.")

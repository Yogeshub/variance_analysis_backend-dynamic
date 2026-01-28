import pandas as pd
import numpy as np

def discover_kpis(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df["ReportingMonth"] = df[date_column].dt.to_period("M")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    kpi = df.groupby("ReportingMonth")[numeric_cols].sum().reset_index()
    kpi["ReportingMonth"] = kpi["ReportingMonth"].astype(str)

    return kpi

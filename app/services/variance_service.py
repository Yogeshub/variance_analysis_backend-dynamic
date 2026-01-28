import pandas as pd
import numpy as np

def compute_variance(kpi_df):
    variance_df = kpi_df.copy()

    for col in kpi_df.columns:
        if col != "ReportingMonth":
            variance_df[f"{col} Change %"] = kpi_df[col].pct_change() * 100

    variance_df = variance_df.replace([np.inf, -np.inf], None)
    variance_df = variance_df.fillna(0)

    return variance_df

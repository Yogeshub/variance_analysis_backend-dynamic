import pandas as pd


def compute_kpis_chunk(df_chunk):
    """Compute KPIs for a single chunk."""
    df_chunk["ReportingMonth"] = df_chunk["Transaction Date"].dt.to_period("M")
    kpi_chunk = (
        df_chunk.groupby("ReportingMonth")
        .agg(
            {
                "Loan ID": "nunique",
                "Transaction Amount": "sum",
                "Account Balance": "mean",
                "Loan Amount": "sum",
            }
        )
        .rename(
            columns={
                "Loan ID": "Total Unique Transactions",
                "Transaction Amount": "Cumulative Transaction Value",
                "Account Balance": "Mean Account Balance",
                "Loan Amount": "Aggregate Loan Disbursed",
            }
        )
        .reset_index()
    )

    # Change %
    for col in kpi_chunk.columns[1:]:
        kpi_chunk[f"{col} Change %"] = kpi_chunk[col].pct_change() * 100

    variance_chunk = kpi_chunk.copy()
    return kpi_chunk, variance_chunk


def merge_kpis(kpi_accum, kpi_chunk):
    """Merge two KPI DataFrames."""
    if kpi_accum is None:
        return kpi_chunk
    return (
        pd.concat([kpi_accum, kpi_chunk], ignore_index=True)
        .groupby("ReportingMonth", as_index=False)
        .sum()
    )

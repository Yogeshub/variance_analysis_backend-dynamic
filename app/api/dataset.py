from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import io
import json
from app.core.database import get_connection

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_ROWS = 100000


def detect_date_column(df):
    for col in df.columns:
        try:
            converted = pd.to_datetime(df[col], errors="coerce")
            if converted.notna().sum() > 0:
                return col
        except:
            continue
    return None


@router.post("/upload")
async def upload_dataset(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit")

    df = pd.read_csv(io.BytesIO(content))

    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty")

    if len(df) > MAX_ROWS:
        raise HTTPException(status_code=400, detail="Row limit exceeded (100,000 max)")

    if df.columns.tolist()[0].startswith("Unnamed"):
        raise HTTPException(status_code=400, detail="No valid headers detected")

    date_column = detect_date_column(df)
    if not date_column:
        raise HTTPException(status_code=400, detail="No date column detected")

    valid_kpis = []
    invalid_kpis = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().sum() > 0:
            valid_kpis.append(col)
        else:
            invalid_kpis.append({"column": col, "reason": "Non-numeric or empty"})

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO datasets (session_id, dataset_json, date_column)
        VALUES (?, ?, ?)
    """, (session_id, df.to_json(), date_column))

    conn.commit()
    conn.close()

    return {
        "message": "File processed successfully",
        "date_column": date_column,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "valid_kpis": valid_kpis,
        "invalid_kpis": invalid_kpis
    }
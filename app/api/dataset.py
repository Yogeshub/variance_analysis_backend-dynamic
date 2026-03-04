from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List, Dict, Any
import pandas as pd
import io
import base64
import json
import os

from app.core.database import get_connection
from app.services.domain_service import detect_domain, detect_subdomains
from app.services.prompt_service import generate_prompt_suggestions
from pydantic import BaseModel

router = APIRouter(tags=["Upload Dataset"])

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


def _load_dataframe_from_bytes(filename: str, content: bytes) -> pd.DataFrame:
    """Load a DataFrame based on filename extension. Supports CSV/TSV/XLS/XLSX."""
    ext = (os.path.splitext(filename)[1] or "").lower()

    if ext in [".csv", ".txt"]:
        # Let pandas infer delimiter; engine='python' supports sep=None sniffing
        return pd.read_csv(io.BytesIO(content), engine="python")
    elif ext in [".tsv"]:
        return pd.read_csv(io.BytesIO(content), sep="\t", engine="python")
    elif ext in [".xlsx", ".xls"]:
        try:
            # openpyxl is required for .xlsx; xlrd for legacy .xls (depending on pandas version)
            return pd.read_excel(io.BytesIO(content), engine="openpyxl" if ext == ".xlsx" else None)
        except ImportError:
            raise HTTPException(
                status_code=400,
                detail="Excel support requires 'openpyxl' installed on the server."
            )
    else:
        # Fallback: try CSV
        try:
            return pd.read_csv(io.BytesIO(content), engine="python")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Please upload CSV/TSV/XLS/XLSX."
            )


def _process_dataset(session_id: str, df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty")

    if len(df) > MAX_ROWS:
        raise HTTPException(status_code=400, detail="Row limit exceeded (100,000 max)")

    # Basic header sanity check
    first_col = df.columns.tolist()[0] if len(df.columns) > 0 else None
    if not first_col or str(first_col).startswith("Unnamed"):
        raise HTTPException(status_code=400, detail="No valid headers detected")

    # Date column detection
    date_column = detect_date_column(df)
    if not date_column:
        raise HTTPException(status_code=400, detail="No date column detected")

    # Domain & subdomain detection
    detected_domains = detect_domain(df)
    subdomain_info = None
    if detected_domains:
        subdomain_info = detect_subdomains(df, detected_domains[0])

    # KPI validation
    valid_kpis: List[str] = []
    invalid_kpis: List[Dict[str, str]] = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().sum() > 0:
            valid_kpis.append(col)
        else:
            invalid_kpis.append({"column": col, "reason": "Non-numeric or empty"})

    detected_subdomain_column = subdomain_info.get("column") if subdomain_info else None

    # Persist minimal dataset + metadata
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO datasets (session_id, dataset_json, date_column, subdomain_column)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, df.to_json(), date_column, detected_subdomain_column),
    )
    conn.commit()
    conn.close()

    return {
        "message": "File processed successfully",
        "detected_domains": detected_domains,
        "subdomain_info": subdomain_info,
        "date_column": date_column,
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "valid_kpis": valid_kpis,
        "invalid_kpis": invalid_kpis,
        "suggested_prompts": generate_prompt_suggestions(detected_domains),
    }



@router.post("/upload")
async def upload_dataset(session_id: str = Form(...), file: UploadFile = File(...)):
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
    # Domain detection
    detected_domains = detect_domain(df)

    # Subdomain detection (use first detected domain)
    subdomain_info = None
    if detected_domains:
        subdomain_info = detect_subdomains(df, detected_domains[0])

    if not date_column:
        raise HTTPException(status_code=400, detail="No date column detected")

    valid_kpis = []
    invalid_kpis = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().sum() > 0:
            valid_kpis.append(col)
        else:
            invalid_kpis.append({"column": col, "reason": "Non-numeric or empty"})

    detected_subdomain_column = subdomain_info.get("column")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO datasets (session_id, dataset_json, date_column,subdomain_column )
        VALUES (?, ?, ?, ?)
    """,
        (session_id, df.to_json(), date_column, detected_subdomain_column),
    )

    conn.commit()
    conn.close()

    return {
        "message": "File processed successfully",
        "detected_domains": detected_domains,
        "subdomain_info": subdomain_info,
        "date_column": date_column,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "valid_kpis": valid_kpis,
        "invalid_kpis": invalid_kpis,
        "suggested_prompts": generate_prompt_suggestions(detected_domains),
    }




class UploadBase64Body(BaseModel):
    session_id: str
    filename: str
    content_base64: str


@router.post("/upload-base64")
def upload_dataset_base64(body: UploadBase64Body):
    """
    Upload a dataset as JSON with base64 content.
    body = {
      "session_id": "...",
      "filename": "data.csv" | "data.xlsx",
      "content_base64": "..."
    }
    """
    # Decode
    try:
        content = base64.b64decode(body.content_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 content")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit after decode")

    df = _load_dataframe_from_bytes(body.filename, content)
    return _process_dataset(body.session_id, df)

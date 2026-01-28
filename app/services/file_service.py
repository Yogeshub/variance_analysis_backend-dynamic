import pandas as pd
import io
from fastapi import HTTPException
import json
import os

DOMAIN_CONFIG_PATH = os.path.join("app", "core", "domain_config.json")

def load_domain_config():
    with open(DOMAIN_CONFIG_PATH) as f:
        return json.load(f)

def parse_file(file_bytes: bytes, filename: str):
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parsing failed: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="File contains no data")

    if not df.columns.tolist():
        raise HTTPException(status_code=400, detail="Missing headers in file")

    df.columns = [c.strip() for c in df.columns]
    return df

def validate_domain(df, domain):
    configs = load_domain_config()
    if domain not in configs:
        raise HTTPException(status_code=400, detail="Invalid domain configuration")

    required = configs[domain]["required_columns"]
    for col in required:
        if col not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file does not match configured domain '{domain}'"
            )

    return configs[domain]

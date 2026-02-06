import pandas as pd
import io
from fastapi import UploadFile, HTTPException
from app.core.config import settings


async def validate_and_read_file(file: UploadFile) -> pd.DataFrame:
    content = await file.read()

    # 1️⃣ File size validation
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        )

    # 2️⃣ Parse CSV / Excel
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parsing failed: {str(e)}")

    # 3️⃣ Header validation
    if df.columns.tolist() == list(range(len(df.columns))):
        raise HTTPException(
            status_code=400, detail="Uploaded file does not contain valid headers"
        )

    if df.empty:
        raise HTTPException(status_code=400, detail="File contains no data")

    # 4️⃣ Row limit validation
    if len(df) > settings.MAX_ROWS:
        raise HTTPException(
            status_code=400, detail=f"File exceeds {settings.MAX_ROWS} row limit"
        )

    # Normalize headers
    df.columns = [str(c).strip() for c in df.columns]

    return df

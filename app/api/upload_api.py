from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.file_service import validate_and_read_file
from app.services.kpi_service import discover_kpis
from app.services.domain_service import detect_domain, detect_subdomains
from app.models.db_models import Dataset
import json

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = await validate_and_read_file(file)

    # 1️⃣ Domain Detection
    detected_domains = detect_domain(df)

    # 2️⃣ Subdomain detection (for mixed process)
    subdomain_info = detect_subdomains(df, detected_domains[0])

    # 3️⃣ KPI Discovery
    valid_kpis, invalid_kpis = discover_kpis(df)

    # 4️⃣ Store metadata in DB
    dataset = Dataset(
        session_id="TEMP",  # session integration later
        filename=file.filename,
        domain=detected_domains[0],
        row_count=len(df),
        column_metadata=json.dumps(
            {
                "columns": df.columns.tolist(),
                "valid_kpis": valid_kpis,
                "invalid_kpis": invalid_kpis,
            }
        ),
    )

    db.add(dataset)
    db.commit()

    return {
        "message": "File processed successfully",
        "detected_domains": detected_domains,
        "subdomain_info": subdomain_info,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "valid_kpis": valid_kpis,
        "invalid_kpis": invalid_kpis,
    }

from fastapi import HTTPException
from app.core.config import get_active_domain

def validate_domain(df):
    domain_name, domain_config = get_active_domain()

    missing = [
        col for col in domain_config["required_columns"]
        if col not in df.columns
    ]

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Configured domain '{domain_name}' requires columns: {missing}"
        )

    return domain_config["date_column"]

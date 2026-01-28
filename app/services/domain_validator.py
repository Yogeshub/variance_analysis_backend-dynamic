from fastapi import HTTPException
from app.core.config import get_active_domain

def validate_domain(df):
    domain_name, domain_config = get_active_domain()
    required = domain_config["required_columns"]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"File does not match configured domain '{domain_name}'. Missing columns: {missing}"
        )

    return domain_config

import json
import os
import pandas as pd


def load_domain_config():
    path = os.path.join("app", "core", "domain_config.json")
    with open(path, "r") as f:
        return json.load(f)


def detect_domain(df: pd.DataFrame):
    config = load_domain_config()
    allowed = config["allowed_domains"]

    detected = []

    for domain_name, domain_info in allowed.items():
        required_cols = domain_info.get("required_columns", [])

        if any(col in df.columns for col in required_cols):
            detected.append(domain_name)

    if not detected:
        detected.append(config["default_domain"])

    return detected


def detect_subdomains(df: pd.DataFrame, domain: str):
    config = load_domain_config()
    domain_info = config["allowed_domains"].get(domain, {})

    candidates = domain_info.get("domain_column_candidates", [])

    for col in candidates:
        if col in df.columns:
            return {"column": col, "values": df[col].dropna().unique().tolist()}

    return None

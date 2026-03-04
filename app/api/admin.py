# admin.py
from fastapi import APIRouter, Query, HTTPException
from app.core.database import get_connection
from datetime import datetime, timezone

router = APIRouter(tags=["Admin"])


def get_pagination(limit: int, offset: int):
    return limit, offset


def to_iso_string(value):
    """
    Convert SQLite/DB timestamp values to RFC 3339 / ISO 8601 strings that Power Apps accepts.
    - If value is a datetime (naive -> assume UTC), serialize to ISO.
    - If value is a string 'YYYY-MM-DD HH:MM:SS[.ffffff]', convert to 'YYYY-MM-DDTHH:MM:SS[.ffffff]Z'.
    - If already ISO-like with 'T', return as-is (add 'Z' if missing tz).
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    s = str(value).strip()

    # Already ISO-like with 'T'
    if 'T' in s:
        # If no timezone indicator, append Z to mark UTC
        if ('Z' in s) or ('+' in s[10:]) or ('-' in s[10:]):
            return s
        return s + 'Z'

    # Convert 'YYYY-MM-DD HH:MM:SS[.ffffff]' -> 'YYYY-MM-DDTHH:MM:SS[.ffffff]Z'
    s = s.replace(' ', 'T')
    return s + 'Z'


@router.get("/sessions")
def get_sessions(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT session_id, created_at
        FROM sessions
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    conn.close()

    # Normalize created_at
    result = []
    for r in rows:
        item = dict(r)
        if "created_at" in item:
            item["created_at"] = to_iso_string(item["created_at"])
        result.append(item)

    return result


@router.get("/datasets")
def get_datasets(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT session_id, date_column, subdomain_column, created_at
        FROM datasets
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        if "created_at" in item:
            item["created_at"] = to_iso_string(item["created_at"])
        result.append(item)

    return result


@router.get("/analysis-results")
def get_analysis_results(
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT session_id, created_at
        FROM analysis_results
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        if "created_at" in item:
            item["created_at"] = to_iso_string(item["created_at"])
        result.append(item)

    return result


@router.get("/chat-history")
def get_chat_history(
    limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, session_id, role, message, created_at
        FROM chat_history
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        if "created_at" in item:
            item["created_at"] = to_iso_string(item["created_at"])
        result.append(item)

    return result


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    # Delete dependent data first
    cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM datasets WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM analysis_results WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    conn.commit()
    conn.close()

    return {"message": f"Session {session_id} deleted successfully"}


@router.delete("/datasets/{session_id}")
def delete_dataset(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM datasets WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

    return {"message": "Dataset deleted"}


@router.delete("/analysis-results/{session_id}")
def delete_analysis_result(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analysis_results WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

    return {"message": "Analysis result deleted"}


@router.delete("/chat-history/{session_id}")
def delete_chat_history(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

    return {"message": "Chat history deleted"}
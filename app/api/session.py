# sessions.py
from fastapi import APIRouter, HTTPException
import uuid
from app.core.database import get_connection
from datetime import datetime, timezone

router = APIRouter(tags=["Session"])


def to_iso_string(value):
    """
    Convert SQLite/DB timestamp values to RFC 3339 / ISO 8601 strings.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    s = str(value).strip()
    if 'T' in s:
        if ('Z' in s) or ('+' in s[10:]) or ('-' in s[10:]):
            return s
        return s + 'Z'
    return s.replace(' ', 'T') + 'Z'


@router.post("/create")
def create_session():
    session_id = str(uuid.uuid4())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
    INSERT INTO sessions (session_id)
    VALUES (?)
    """,
        (session_id,),
    )

    conn.commit()
    conn.close()

    return {"session_id": session_id, "message": "Session created successfully"}


@router.get("/{session_id}")
def get_session(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT session_id, created_at
        FROM sessions
        WHERE session_id = ?
    """,
        (session_id,),
    )

    session = cursor.fetchone()
    conn.close()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session["session_id"],
        "created_at": to_iso_string(session["created_at"]),
    }


@router.get("/")
def list_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT session_id, created_at
        FROM sessions
        ORDER BY created_at DESC
    """
    )

    sessions = cursor.fetchall()
    conn.close()

    return [
        {
            "session_id": row["session_id"],
            "created_at": to_iso_string(row["created_at"]),
        }
        for row in sessions
    ]
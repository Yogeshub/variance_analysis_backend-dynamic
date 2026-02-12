from fastapi import APIRouter
import uuid
from app.core.database import get_connection

router = APIRouter(tags=["Session"])


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

    return {"session_id": session["session_id"], "created_at": session["created_at"]}


@router.get("/")
def list_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT session_id, created_at
        FROM sessions
        ORDER BY created_at DESC
    """)

    sessions = cursor.fetchall()
    conn.close()

    return [
        {"session_id": row["session_id"], "created_at": row["created_at"]}
        for row in sessions
    ]

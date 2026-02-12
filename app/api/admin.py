from fastapi import APIRouter, Query, HTTPException
from app.core.database import get_connection

router = APIRouter(tags=["Admin"])


def get_pagination(limit: int, offset: int):
    return limit, offset


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

    return rows


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

    return rows


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

    return rows


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

    return rows


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


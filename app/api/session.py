from fastapi import APIRouter
import uuid
from app.core.database import get_connection

router = APIRouter()

@router.post("/create")
def create_session():
    session_id = str(uuid.uuid4())

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (session_id) VALUES (?)", (session_id,))
    conn.commit()
    conn.close()

    return {"session_id": session_id}

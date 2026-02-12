from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_connection

router = APIRouter(prefix="/prompts", tags=["Prompt Templates"])


class PromptCreate(BaseModel):
    domain: Optional[str] = None
    prompt_type: str  # base / domain
    prompt_text: str


class PromptUpdate(BaseModel):
    domain: Optional[str] = None
    prompt_type: Optional[str] = None
    prompt_text: Optional[str] = None


@router.post("/")
def add_prompt(prompt: PromptCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO prompt_templates (domain, prompt_type, prompt_text)
        VALUES (?, ?, ?)
    """,
        (prompt.domain, prompt.prompt_type, prompt.prompt_text),
    )

    conn.commit()
    prompt_id = cursor.lastrowid
    conn.close()

    return {"id": prompt_id, "message": "Prompt template added successfully"}


@router.put("/{prompt_id}")
def update_prompt(prompt_id: int, payload: PromptUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM prompt_templates WHERE id = ?
    """,
        (prompt_id,),
    )

    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Prompt not found")

    fields = []
    values = []

    if payload.domain is not None:
        fields.append("domain = ?")
        values.append(payload.domain)

    if payload.prompt_type is not None:
        fields.append("prompt_type = ?")
        values.append(payload.prompt_type)

    if payload.prompt_text is not None:
        fields.append("prompt_text = ?")
        values.append(payload.prompt_text)

    if not fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(prompt_id)

    cursor.execute(
        f"""
        UPDATE prompt_templates
        SET {", ".join(fields)}
        WHERE id = ?
    """,
        values,
    )

    conn.commit()
    conn.close()

    return {"message": "Prompt template updated successfully"}


@router.get("/")
def list_prompts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, domain, prompt_type, prompt_text
        FROM prompt_templates
        ORDER BY prompt_type, domain
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "domain": row["domain"],
            "prompt_type": row["prompt_type"],
            "prompt_text": row["prompt_text"],
        }
        for row in rows
    ]


@router.get("/domain/{domain}")
def get_prompts_by_domain(domain: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, prompt_type, prompt_text
        FROM prompt_templates
        WHERE domain = ? OR prompt_type = 'base'
    """,
        (domain,),
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM prompt_templates WHERE id = ?
    """,
        (prompt_id,),
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Prompt not found")

    conn.commit()
    conn.close()

    return {"message": "Prompt template deleted successfully"}

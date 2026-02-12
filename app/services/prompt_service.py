from app.core.database import get_connection


def generate_prompt_suggestions(domain, selected_kpis=None):
    conn = get_connection()
    cursor = conn.cursor()

    # Base prompts
    cursor.execute("""
        SELECT prompt_text FROM prompt_templates
        WHERE prompt_type='base'
    """)
    base_prompts = [row["prompt_text"] for row in cursor.fetchall()]

    # Domain prompts
    domain_prompts = []
    if domain:
        if isinstance(domain, list):
            placeholders = ",".join(["?"] * len(domain))
            cursor.execute(
                f"""
                SELECT prompt_text FROM prompt_templates
                WHERE prompt_type='domain' AND domain IN ({placeholders})
                """,
                domain,
            )
        else:
            cursor.execute(
                """
                SELECT prompt_text FROM prompt_templates
                WHERE prompt_type='domain' AND domain=?
                """,
                (domain,),
            )

        domain_prompts = [row["prompt_text"] for row in cursor.fetchall()]

    conn.close()

    kpi_specific = []
    if selected_kpis:
        for kpi in selected_kpis:
            kpi_specific.append(f"Explain trend of {kpi}")
            kpi_specific.append(f"Is {kpi} increasing risk?")

    return list(set(base_prompts + domain_prompts + kpi_specific))

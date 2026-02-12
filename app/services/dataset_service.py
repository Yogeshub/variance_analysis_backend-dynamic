# import pandas as pd
# import json
# from app.core.database import get_connection
#
#
# class DatasetService:
#
#     @staticmethod
#     def save_dataset(session_id: str, df: pd.DataFrame):
#         conn = get_connection()
#         cursor = conn.cursor()
#
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS datasets (
#             session_id TEXT PRIMARY KEY,
#             data TEXT
#         )
#         """)
#
#         data_json = df.to_json(orient="records")
#
#         cursor.execute("""
#         INSERT OR REPLACE INTO datasets (session_id, data)
#         VALUES (?, ?)
#         """, (session_id, data_json))
#
#         conn.commit()
#         conn.close()
#
#     @staticmethod
#     def load_dataset(session_id: str):
#         conn = get_connection()
#         cursor = conn.cursor()
#
#         cursor.execute("""
#         SELECT data FROM datasets WHERE session_id = ?
#         """, (session_id,))
#
#         row = cursor.fetchone()
#         conn.close()
#
#         if not row:
#             return None
#
#         data = json.loads(row[0])
#         return pd.DataFrame(data)
import sqlite3
import os
import pandas as pd

DB_PATH = "variance.db"


class DatasetService:

    @staticmethod
    def save_dataset(session_id: str, df: pd.DataFrame):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO datasets (session_id, data_json)
            VALUES (?, ?)
        """,
            (session_id, df.to_json()),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def load_dataset(session_id: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT data_json FROM datasets WHERE session_id = ?
        """,
            (session_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return pd.read_json(row[0])

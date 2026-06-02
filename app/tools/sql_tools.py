import re
import sqlite3
from pathlib import Path
from typing import Any

from app.config import DB_PATH, ROOT_DIR


BLOCKED_SQL = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create|replace|attach|detach|pragma)\b", re.I)


class SQLSafetyError(ValueError):
    pass


def validate_select_only(query: str) -> str:
    cleaned = query.strip().rstrip(";")
    if not cleaned.lower().startswith("select"):
        raise SQLSafetyError("Only SELECT statements are allowed.")
    if BLOCKED_SQL.search(cleaned):
        raise SQLSafetyError("Mutating or administrative SQL statements are not allowed.")
    if ";" in cleaned:
        raise SQLSafetyError("Multiple SQL statements are not allowed.")
    return cleaned


def initialize_database(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema = (ROOT_DIR / "data" / "sql" / "schema.sql").read_text(encoding="utf-8")
    seed = (ROOT_DIR / "data" / "sql" / "seed.sql").read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        conn.executescript(seed)


def execute_select(query: str, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    safe_query = validate_select_only(query)
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(safe_query).fetchall()
    return [dict(row) for row in rows]


def question_to_sql(question: str) -> str:
    q = question.lower()
    if "failed" in q or "error" in q:
        return (
            "SELECT batch_id, template_code, status, error_code, created_at "
            "FROM letter_batches WHERE status = 'FAILED' ORDER BY created_at DESC LIMIT 10"
        )
    if "preference" in q:
        return "SELECT user_id, response_style, preferred_agent, preferred_detail_level FROM user_preferences"
    if "status" in q:
        return "SELECT batch_id, template_code, status, created_at FROM letter_batches ORDER BY created_at DESC LIMIT 10"
    if "customer" in q:
        return "SELECT customer_id, segment, communication_preference FROM mock_customers LIMIT 10"
    return "SELECT batch_id, template_code, status, created_at FROM letter_batches ORDER BY created_at DESC LIMIT 5"


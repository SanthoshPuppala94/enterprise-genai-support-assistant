import sqlite3
from pathlib import Path

from app.config import DB_PATH


class PreferenceStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    response_style TEXT DEFAULT 'concise',
                    preferred_agent TEXT DEFAULT '',
                    preferred_detail_level TEXT DEFAULT 'medium'
                )
                """
            )

    def save_preferences(
        self,
        user_id: str,
        response_style: str = "concise",
        preferred_agent: str = "",
        preferred_detail_level: str = "medium",
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO user_preferences (user_id, response_style, preferred_agent, preferred_detail_level)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    response_style = excluded.response_style,
                    preferred_agent = excluded.preferred_agent,
                    preferred_detail_level = excluded.preferred_detail_level
                """,
                (user_id, response_style, preferred_agent, preferred_detail_level),
            )

    def get_preferences(self, user_id: str) -> dict[str, str]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT user_id, response_style, preferred_agent, preferred_detail_level
                FROM user_preferences
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        if not row:
            return {}
        return dict(row)


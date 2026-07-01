import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "ap_socratic.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id TEXT NOT NULL,
                unit_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                visible INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_unit
            ON messages (subject_id, unit_id, id)
        """)


def get_conversation(subject_id: str, unit_id: str) -> list[dict]:
    """Full history (including invisible scaffold turns) in API message order."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content, visible FROM messages "
            "WHERE subject_id = ? AND unit_id = ? ORDER BY id",
            (subject_id, unit_id),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"], "visible": bool(r["visible"])} for r in rows]


def append_message(subject_id: str, unit_id: str, role: str, content: str, visible: bool = True):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (subject_id, unit_id, role, content, visible) VALUES (?, ?, ?, ?, ?)",
            (subject_id, unit_id, role, content, int(visible)),
        )

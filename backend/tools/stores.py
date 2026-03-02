"""Local-first stores for KB search and ticket persistence."""

from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_\u4e00-\u9fff]+", text.lower())


class FAQStore:
    """Simple JSON-based FAQ/KB search store."""

    def __init__(self, kb_path: str):
        self.kb_path = Path(kb_path)
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.kb_path.exists():
            self.kb_path.write_text("[]", encoding="utf-8")

    def _load(self) -> List[Dict[str, Any]]:
        try:
            content = self.kb_path.read_text(encoding="utf-8")
            data = json.loads(content)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        items = self._load()
        q_tokens = set(_tokenize(query))
        scored = []
        for item in items:
            haystack = " ".join(
                [
                    str(item.get("question", "")),
                    str(item.get("answer", "")),
                    " ".join(item.get("tags", []) or []),
                ]
            )
            item_tokens = set(_tokenize(haystack))
            overlap = len(q_tokens.intersection(item_tokens))
            if overlap == 0:
                continue
            scored.append((overlap, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in scored[: max(1, top_k)]]


class TicketStore:
    """SQLite-backed ticket persistence."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id)")
            conn.commit()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "ticket_id": row["ticket_id"],
            "user_id": row["user_id"],
            "subject": row["subject"],
            "description": row["description"],
            "priority": row["priority"],
            "tags": json.loads(row["tags_json"] or "[]"),
            "status": row["status"],
            "created_at": float(row["created_at"]),
            "updated_at": float(row["updated_at"]),
        }

    def create_ticket(
        self,
        user_id: str,
        subject: str,
        description: str,
        priority: str,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        now = time.time()
        ticket_id = f"T{uuid.uuid4().hex[:10].upper()}"
        tags = tags or []
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tickets(ticket_id, user_id, subject, description, priority, tags_json, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket_id,
                    user_id,
                    subject,
                    description,
                    priority,
                    json.dumps(tags),
                    "open",
                    now,
                    now,
                ),
            )
            conn.commit()
        return self.get_ticket(ticket_id) or {}

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
            row = cur.fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def list_tickets(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT * FROM tickets
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, max(1, limit)),
            )
            rows = cur.fetchall()
        return [self._row_to_dict(row) for row in rows]


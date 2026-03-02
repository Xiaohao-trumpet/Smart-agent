"""SQLite repository for long-term memory records."""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


@dataclass
class MemoryRow:
    """Persisted memory row."""

    id: str
    user_id: str
    text: str
    tags: List[str]
    created_at: float
    updated_at: float
    metadata: Dict[str, Any]


class MemoryRepository:
    """CRUD access for memory rows stored in local SQLite."""

    def __init__(self, db_path: str):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_user ON memory_items(user_id)"
            )
            conn.commit()

    @staticmethod
    def _to_row(record: sqlite3.Row) -> MemoryRow:
        return MemoryRow(
            id=record["id"],
            user_id=record["user_id"],
            text=record["text"],
            tags=json.loads(record["tags_json"] or "[]"),
            metadata=json.loads(record["metadata_json"] or "{}"),
            created_at=float(record["created_at"]),
            updated_at=float(record["updated_at"]),
        )

    def add(
        self,
        memory_id: str,
        user_id: str,
        text: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRow:
        now = time.time()
        tags = tags or []
        metadata = metadata or {}
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO memory_items (id, user_id, text, tags_json, metadata_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (memory_id, user_id, text, json.dumps(tags), json.dumps(metadata), now, now),
                )
                conn.commit()
        return self.get(memory_id)  # type: ignore[return-value]

    def list_by_user(self, user_id: str) -> List[MemoryRow]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT * FROM memory_items
                WHERE user_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
        return [self._to_row(row) for row in rows]

    def get(self, memory_id: str) -> Optional[MemoryRow]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT * FROM memory_items WHERE id = ?",
                (memory_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return self._to_row(row)

    def get_many(self, memory_ids: List[str]) -> Dict[str, MemoryRow]:
        if not memory_ids:
            return {}
        placeholders = ",".join(["?"] * len(memory_ids))
        with self._connect() as conn:
            cur = conn.execute(
                f"SELECT * FROM memory_items WHERE id IN ({placeholders})",
                tuple(memory_ids),
            )
            rows = cur.fetchall()
        parsed = [self._to_row(row) for row in rows]
        return {row.id: row for row in parsed}

    def update(
        self,
        memory_id: str,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[MemoryRow]:
        existing = self.get(memory_id)
        if existing is None:
            return None

        new_text = text if text is not None else existing.text
        new_tags = tags if tags is not None else existing.tags
        new_metadata = metadata if metadata is not None else existing.metadata

        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    UPDATE memory_items
                    SET text = ?, tags_json = ?, metadata_json = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        new_text,
                        json.dumps(new_tags),
                        json.dumps(new_metadata),
                        time.time(),
                        memory_id,
                    ),
                )
                conn.commit()

        return self.get(memory_id)

    def delete(self, memory_id: str) -> bool:
        with self._lock:
            with self._connect() as conn:
                cur = conn.execute(
                    "DELETE FROM memory_items WHERE id = ?",
                    (memory_id,),
                )
                conn.commit()
                return cur.rowcount > 0


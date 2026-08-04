"""Memória do Jarvis: histórico de conversa + factos de longo prazo.

Usa SQLite (biblioteca padrão) — não requer instalação de nada.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable


class Memory:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                role    TEXT NOT NULL,
                content TEXT NOT NULL,
                ts      TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS facts (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                key     TEXT UNIQUE,
                value   TEXT NOT NULL,
                ts      TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    # --- Histórico de conversa ---
    def add_message(self, role: str, content: str) -> None:
        self.conn.execute(
            "INSERT INTO messages (role, content, ts) VALUES (?, ?, ?)",
            (role, content, datetime.utcnow().isoformat()),
        )
        self.conn.commit()

    def recent_messages(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def clear_messages(self) -> None:
        self.conn.execute("DELETE FROM messages")
        self.conn.commit()

    # --- Factos de longo prazo (o que o Jarvis "sabe" sobre ti) ---
    def remember(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO facts (key, value, ts) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, ts=excluded.ts",
            (key, value, datetime.utcnow().isoformat()),
        )
        self.conn.commit()

    def recall(self, key: str | None = None) -> list[dict]:
        if key:
            rows = self.conn.execute(
                "SELECT key, value FROM facts WHERE key LIKE ?", (f"%{key}%",)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT key, value FROM facts").fetchall()
        return [{"key": r["key"], "value": r["value"]} for r in rows]

    def facts_summary(self) -> str:
        facts = self.recall()
        if not facts:
            return ""
        lines = "\n".join(f"- {f['key']}: {f['value']}" for f in facts)
        return f"Factos que sabes sobre o utilizador:\n{lines}"

    def close(self) -> None:
        self.conn.close()

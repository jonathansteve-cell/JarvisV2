"""Persistent memory and learning for Jarvis V2."""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MemoryController:
    """SQLite-backed assistant memory."""

    def __init__(self, config: Any) -> None:
        self.config = config
        data_dir = Path(config.get("paths.data_dir", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / "jarvis_memory.sqlite3"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    intent TEXT,
                    success INTEGER,
                    created_at TEXT NOT NULL
                )
                """
            )

    def remember(self, key: str, value: str, category: str = "general") -> str:
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO facts(key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    category=excluded.category,
                    updated_at=excluded.updated_at
                """,
                (key, value, category, datetime.now().isoformat(timespec="seconds")),
            )
        return f"I will remember that {key.replace('_', ' ')} is {value}, sir."

    def recall(self, query: str = "") -> list[dict[str, str]]:
        with self._connect() as conn:
            if query:
                like = f"%{query.lower()}%"
                rows = conn.execute(
                    "SELECT key, value, category, updated_at FROM facts WHERE key LIKE ? OR value LIKE ? ORDER BY updated_at DESC LIMIT 20",
                    (like, like),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT key, value, category, updated_at FROM facts ORDER BY updated_at DESC LIMIT 20"
                ).fetchall()
        return [dict(row) for row in rows]

    def forget(self, query: str) -> str:
        key = query.strip().lower().replace(" ", "_")
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM facts WHERE key=?", (key,))
        if cur.rowcount:
            return f"I have forgotten {query}, sir."
        return f"I could not find a memory named {query}, sir."

    def save_conversation(self, command: str, response: str) -> None:
        if not self.config.get("behavior.remember_conversations", True):
            return
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations(command, response, created_at) VALUES (?, ?, ?)",
                (command, response, datetime.now().isoformat(timespec="seconds")),
            )

    def log_interaction(self, command: str, intent: str, success: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO interactions(command, intent, success, created_at) VALUES (?, ?, ?, ?)",
                (command, intent, int(success), datetime.now().isoformat(timespec="seconds")),
            )

    def learn_from_command(self, command: str) -> str | None:
        """Extract simple facts like 'my name is Alex' or 'I prefer dark mode'."""
        if not self.config.get("behavior.learning_enabled", True):
            return None
        patterns = [
            (r"my name is ([\w .'-]+)", "name", "identity"),
            (r"call me ([\w .'-]+)", "preferred_name", "identity"),
            (r"i prefer (.+)", "preference", "preference"),
            (r"i like (.+)", "likes", "preference"),
            (r"i work as (?:a |an )?(.+)", "profession", "identity"),
        ]
        lower = command.lower()
        for pattern, key, category in patterns:
            match = re.search(pattern, lower)
            if match:
                return self.remember(key, match.group(1).strip(), category)
        return None

    def memory_context(self) -> str:
        facts = self.recall()
        if not facts:
            return "No persistent facts stored yet."
        return "\n".join(f"- {f['key']}: {f['value']}" for f in facts[:10])

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            facts = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
            conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            interactions = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        return {"facts": facts, "conversations": conversations, "interactions": interactions}

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        if lower.startswith("remember "):
            payload = command.split(" ", 1)[1].strip()
            if " is " in payload:
                key, value = payload.split(" is ", 1)
            elif ":" in payload:
                key, value = payload.split(":", 1)
            else:
                key, value = "note", payload
            return {"success": True, "response": self.remember(key, value)}
        if lower.startswith("forget "):
            return {"success": True, "response": self.forget(command.split(" ", 1)[1])}
        if "what do you remember" in lower or "show memory" in lower:
            facts = self.recall()
            if not facts:
                return {"success": True, "response": "I do not have any stored memories yet, sir."}
            response = "Here is what I remember, sir: " + "; ".join(
                f"{f['key'].replace('_', ' ')} is {f['value']}" for f in facts[:8]
            )
            return {"success": True, "response": response, "data": facts}
        if "memory stats" in lower:
            stats = self.stats()
            return {
                "success": True,
                "response": (
                    f"Memory contains {stats['facts']} facts, {stats['conversations']} conversations, "
                    f"and {stats['interactions']} logged interactions, sir."
                ),
                "data": stats,
            }
        rename = re.search(r"(?:your name is|change your name to|i will call you|i call you) ([\w .'-]+)", lower)
        if rename:
            name = rename.group(1).strip()
            if name:
                self.remember("assistant_name", name, "identity")
                return {"success": True, "response": f"Very well, sir. You may call me {name.title()} from now on."}
        learned = self.learn_from_command(command)
        if learned:
            return {"success": True, "response": learned}
        return {"success": False, "response": "I did not find a memory command, sir."}

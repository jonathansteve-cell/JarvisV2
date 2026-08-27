"""Notes, reminders, tasks, and timers."""

from __future__ import annotations

import json
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.helpers import parse_delay


class ProductivityController:
    """Local productivity storage and timer engine."""

    def __init__(self, config: Any) -> None:
        self.config = config
        data_dir = Path(config.get("paths.data_dir", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "productivity.json"
        self.data = {"notes": [], "tasks": [], "reminders": []}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self.data.update(json.loads(self.path.read_text(encoding="utf-8")))

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def add_note(self, text: str) -> str:
        self.data["notes"].append({"text": text.strip(), "created_at": datetime.now().isoformat()})
        self._save()
        return "Note recorded, sir."

    def add_task(self, text: str) -> str:
        self.data["tasks"].append(
            {"text": text.strip(), "done": False, "created_at": datetime.now().isoformat()}
        )
        self._save()
        return f"Task added: {text.strip()}"

    def list_tasks(self) -> str:
        tasks = [task for task in self.data["tasks"] if not task.get("done")]
        if not tasks:
            return "You have no open tasks, sir."
        return "Open tasks: " + "; ".join(task["text"] for task in tasks[:10])

    def add_reminder(self, text: str, due_at: datetime | None) -> str:
        self.data["reminders"].append(
            {
                "text": text.strip(),
                "due_at": due_at.isoformat() if due_at else None,
                "done": False,
                "created_at": datetime.now().isoformat(),
            }
        )
        self._save()
        if due_at:
            return f"Reminder set for {due_at.strftime('%Y-%m-%d %I:%M %p')}, sir."
        return "Reminder saved, sir."

    def list_reminders(self) -> str:
        reminders = [item for item in self.data["reminders"] if not item.get("done")]
        if not reminders:
            return "No active reminders, sir."
        parts = []
        for reminder in reminders[:10]:
            due = reminder.get("due_at") or "no due time"
            parts.append(f"{reminder['text']} at {due}")
        return "Your reminders are: " + "; ".join(parts)

    def set_timer(self, seconds: int, label: str = "timer") -> str:
        def notify() -> None:
            # The main app owns voice output; this updates stored reminders as a fallback.
            self.data["reminders"].append(
                {
                    "text": f"Timer finished: {label}",
                    "due_at": datetime.now().isoformat(),
                    "done": False,
                    "created_at": datetime.now().isoformat(),
                }
            )
            self._save()

        threading.Timer(seconds, notify).start()
        return f"Timer set for {seconds} seconds, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        if lower.startswith("take note") or lower.startswith("note "):
            text = re.sub(r"^(take note|note)[: ]*", "", command, flags=re.I).strip()
            return {"success": True, "response": self.add_note(text)}
        if lower.startswith("add task") or lower.startswith("create task"):
            text = re.sub(r"^(add task|create task)[: ]*", "", command, flags=re.I).strip()
            return {"success": True, "response": self.add_task(text)}
        if "show tasks" in lower or "list tasks" in lower or "my tasks" in lower:
            return {"success": True, "response": self.list_tasks(), "data": self.data["tasks"]}
        if lower.startswith("remind me"):
            due = parse_delay(lower)
            text = re.sub(r"^remind me( to)?", "", command, flags=re.I).strip()
            return {"success": True, "response": self.add_reminder(text, due)}
        if "show reminders" in lower or "list reminders" in lower or "my reminders" in lower:
            return {"success": True, "response": self.list_reminders(), "data": self.data["reminders"]}
        timer_match = re.search(r"timer (?:for )?(\d+)\s*(second|seconds|minute|minutes|hour|hours)", lower)
        if timer_match:
            amount = int(timer_match.group(1))
            unit = timer_match.group(2)
            seconds = amount * (3600 if unit.startswith("hour") else 60 if unit.startswith("minute") else 1)
            return {"success": True, "response": self.set_timer(seconds)}
        return {"success": False, "response": "I did not find a productivity command, sir."}

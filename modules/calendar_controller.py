"""Calendar integration with local fallback."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class CalendarController:
    """Manage a local calendar; ready for Google Calendar credentials if added later."""

    def __init__(self, config: Any) -> None:
        self.config = config
        data_dir = Path(config.get("paths.data_dir", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "calendar_events.json"
        self.events: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self.events = json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.events, indent=2), encoding="utf-8")

    def add_event(self, title: str, when: str = "today") -> str:
        start = datetime.now() + timedelta(hours=1)
        self.events.append({"title": title.strip(), "when": when, "start": start.isoformat(), "created_at": datetime.now().isoformat()})
        self._save()
        return f"Calendar event added: {title.strip()}, sir."

    def list_events(self) -> str:
        if not self.events:
            return "Your local calendar has no events, sir."
        upcoming = self.events[-8:]
        return "Upcoming calendar items: " + "; ".join(item["title"] for item in upcoming)

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        if "calendar" not in lower and "schedule" not in lower and "meeting" not in lower:
            return {"success": False, "response": "I did not find a calendar command, sir."}
        add_match = re.search(r"(?:add|create|schedule).*(?:calendar|event|meeting)[: ]+(.+)", command, re.I)
        if add_match:
            return {"success": True, "response": self.add_event(add_match.group(1))}
        if "what" in lower or "show" in lower or "today" in lower or "schedule" in lower:
            return {"success": True, "response": self.list_events(), "data": self.events}
        return {"success": False, "response": "I did not find a calendar command, sir."}

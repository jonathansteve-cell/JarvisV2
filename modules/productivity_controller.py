"""Notes, reminders, tasks, and timers.

Reminders are stored in ``data/productivity.json`` *and* actually fired: call
``start_notifier(callback)`` (``core/jarvis.py`` does this at boot) and a daemon
thread sweeps the list on an interval, invoking the callback for every reminder
whose ``due_at`` has passed and marking it done so it only fires once.
"""

from __future__ import annotations

import json
import logging
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from utils.helpers import parse_delay

logger = logging.getLogger(__name__)

#: Seconds between sweeps for due reminders.
DEFAULT_SWEEP_INTERVAL = 20.0


class ProductivityController:
    """Local productivity storage, timer engine, and reminder notifier."""

    def __init__(self, config: Any) -> None:
        self.config = config
        data_dir = Path(config.get("paths.data_dir", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "productivity.json"
        self.data: dict[str, Any] = {"notes": [], "tasks": [], "reminders": []}
        self._lock = threading.RLock()
        self._notifier: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._callback: Callable[[str], None] | None = None
        self._load()

    # --------------------------------------------------------------- storage
    def _load(self) -> None:
        if self.path.exists():
            try:
                with self._lock:
                    self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Could not read %s: %s", self.path, exc)

    def _save(self) -> None:
        with self._lock:
            self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    # ----------------------------------------------------------------- notes
    def add_note(self, text: str) -> str:
        with self._lock:
            self.data["notes"].append({"text": text.strip(), "created_at": datetime.now().isoformat()})
        self._save()
        return "Note recorded, sir."

    def add_task(self, text: str) -> str:
        with self._lock:
            self.data["tasks"].append(
                {"text": text.strip(), "done": False, "created_at": datetime.now().isoformat()}
            )
        self._save()
        return f"Task added: {text.strip()}"

    def list_tasks(self) -> str:
        with self._lock:
            tasks = [task for task in self.data["tasks"] if not task.get("done")]
        if not tasks:
            return "You have no open tasks, sir."
        return "Open tasks: " + "; ".join(task["text"] for task in tasks[:10])

    def _find_task(self, text: str) -> dict[str, Any] | None:
        """Exact match first, then substring in either direction."""
        needle = text.strip().lower()
        if not needle:
            return None
        with self._lock:
            for task in self.data["tasks"]:
                if task["text"].lower() == needle:
                    return task
            for task in self.data["tasks"]:
                stored = task["text"].lower()
                if needle in stored or stored in needle:
                    return task
        return None

    def complete_task(self, text: str, done: bool = True) -> str:
        """Mark the closest-matching task done, or reopen it."""
        if not text.strip():
            return "Which task should I update, sir?"
        task = self._find_task(text)
        if task is None:
            return f"I could not find a task matching '{text.strip()}', sir."
        with self._lock:
            task["done"] = done
            task["completed_at"] = datetime.now().isoformat() if done else None
            label = task["text"]
        self._save()
        return f"Marked done: {label}" if done else f"Reopened: {label}"

    def remove_task(self, text: str) -> str:
        """Delete a task outright."""
        task = self._find_task(text)
        if task is None:
            return f"I could not find a task matching '{text.strip()}', sir."
        with self._lock:
            self.data["tasks"] = [item for item in self.data["tasks"] if item is not task]
            label = task["text"]
        self._save()
        return f"Task removed: {label}"

    # ------------------------------------------------------------- reminders
    def add_reminder(self, text: str, due_at: datetime | None) -> str:
        with self._lock:
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
        return (
            f"Reminder saved without a time, sir — I could not work out when you meant. "
            f"Try 'remind me to {text.strip()} at 6pm' or 'in 30 minutes'."
        )

    def list_reminders(self) -> str:
        with self._lock:
            reminders = [item for item in self.data["reminders"] if not item.get("done")]
        if not reminders:
            return "No active reminders, sir."
        parts = []
        for reminder in reminders[:10]:
            due = reminder.get("due_at")
            when = "no due time"
            if due:
                try:
                    when = datetime.fromisoformat(due).strftime("%Y-%m-%d %I:%M %p")
                except ValueError:
                    when = due
            parts.append(f"{reminder['text']} at {when}")
        return "Your reminders are: " + "; ".join(parts)

    def due_reminders(self, now: datetime | None = None) -> list[dict[str, Any]]:
        """Every reminder whose due time has passed and has not fired yet."""
        now = now or datetime.now()
        due: list[dict[str, Any]] = []
        with self._lock:
            for reminder in self.data["reminders"]:
                if reminder.get("done") or not reminder.get("due_at"):
                    continue
                try:
                    when = datetime.fromisoformat(reminder["due_at"])
                except (ValueError, TypeError):
                    continue
                if when <= now:
                    due.append(reminder)
        return due

    def mark_done(self, reminder: dict[str, Any]) -> None:
        with self._lock:
            reminder["done"] = True
            reminder["fired_at"] = datetime.now().isoformat()
        self._save()

    def sweep_due(self) -> list[str]:
        """One pass: notify and complete every overdue reminder. Returns the texts."""
        fired: list[str] = []
        for reminder in self.due_reminders():
            text = reminder.get("text", "reminder")
            fired.append(text)
            if self._callback:
                try:
                    self._callback(text)
                except Exception:
                    logger.exception("Reminder callback failed for %r", text)
            self.mark_done(reminder)
        return fired

    def start_notifier(self, callback: Callable[[str], None], interval: float = DEFAULT_SWEEP_INTERVAL) -> None:
        """Start the background sweeper. Safe to call more than once."""
        self._callback = callback
        if self._notifier and self._notifier.is_alive():
            return
        self._stop_event.clear()

        def loop() -> None:
            while not self._stop_event.wait(interval):
                try:
                    self.sweep_due()
                except Exception:  # pragma: no cover - defensive
                    logger.exception("Reminder sweep failed")

        self._notifier = threading.Thread(target=loop, name="jarvis-reminders", daemon=True)
        self._notifier.start()
        logger.debug("Reminder notifier started (every %ss)", interval)

    def stop_notifier(self) -> None:
        self._stop_event.set()
        if self._notifier:
            self._notifier.join(timeout=2)
            self._notifier = None

    # ---------------------------------------------------------------- timers
    def set_timer(self, seconds: int, label: str = "timer") -> str:
        def notify() -> None:
            text = f"Timer finished: {label}"
            with self._lock:
                self.data["reminders"].append(
                    {
                        "text": text,
                        "due_at": datetime.now().isoformat(),
                        "done": True,
                        "fired_at": datetime.now().isoformat(),
                        "created_at": datetime.now().isoformat(),
                    }
                )
            self._save()
            if self._callback:
                try:
                    self._callback(label)
                except Exception:
                    logger.exception("Timer callback failed for %r", label)

        threading.Timer(seconds, notify).start()
        return f"Timer set for {seconds} seconds, sir."

    # ---------------------------------------------------------------- router
    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        if lower.startswith("take note") or lower.startswith("note "):
            text = re.sub(r"^(take note|note)[: ]*", "", command, flags=re.I).strip()
            return {"success": True, "response": self.add_note(text)}
        if lower.startswith("add task") or lower.startswith("create task"):
            text = re.sub(r"^(add task|create task)[: ]*", "", command, flags=re.I).strip()
            return {"success": True, "response": self.add_task(text)}
        # Longest prefixes first so "mark task done" is not eaten by "mark task".
        if lower.startswith(("complete task", "finish task", "mark task done", "done task", "mark task")):
            text = re.sub(
                r"^(complete task|finish task|mark task done|done task|mark task)[: ]*",
                "",
                command,
                flags=re.I,
            ).strip()
            return {"success": True, "response": self.complete_task(text)}
        if lower.startswith(("reopen task", "undo task")):
            text = re.sub(r"^(reopen task|undo task)[: ]*", "", command, flags=re.I).strip()
            return {"success": True, "response": self.complete_task(text, done=False)}
        if lower.startswith(("delete task", "remove task")):
            text = re.sub(r"^(delete task|remove task)[: ]*", "", command, flags=re.I).strip()
            return {"success": True, "response": self.remove_task(text)}
        if "show tasks" in lower or "list tasks" in lower or "my tasks" in lower:
            return {"success": True, "response": self.list_tasks(), "data": self.data["tasks"]}
        if lower.startswith("remind me"):
            # Parse the time from the whole phrase, not just the tail.
            due = parse_delay(lower)
            text = re.sub(r"^remind me( to)?", "", command, flags=re.I).strip()
            text = re.sub(r"\s+(in \d+\s*\w+|at .+|tomorrow.*)$", "", text, flags=re.I).strip()
            return {"success": True, "response": self.add_reminder(text, due)}
        if "show reminders" in lower or "list reminders" in lower or "my reminders" in lower:
            return {"success": True, "response": self.list_reminders(), "data": self.data["reminders"]}
        if "due reminders" in lower or "any reminders due" in lower:
            fired = self.sweep_due()
            if fired:
                return {"success": True, "response": "Reminders due: " + "; ".join(fired)}
            return {"success": True, "response": "Nothing is due right now, sir."}
        timer_match = re.search(r"timer (?:for )?(\d+)\s*(second|seconds|minute|minutes|hour|hours)", lower)
        if timer_match:
            amount = int(timer_match.group(1))
            unit = timer_match.group(2)
            seconds = amount * (3600 if unit.startswith("hour") else 60 if unit.startswith("minute") else 1)
            label_match = re.search(r"(?:called|named|for) ([a-z ]+)$", lower)
            label = label_match.group(1).strip() if label_match else "timer"
            return {"success": True, "response": self.set_timer(seconds, label)}
        return {"success": False, "response": "I did not find a productivity command, sir."}

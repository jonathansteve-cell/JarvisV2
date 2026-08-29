"""General helper functions."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable


def normalize_command(command: str) -> str:
    """Normalize user command text for routing."""
    command = command.strip().lower()
    command = re.sub(r"\s+", " ", command)
    return command


def remove_wake_word(command: str, wake_words: Iterable[str]) -> str:
    """Remove a wake word prefix if present."""
    text = command.strip()
    lower = text.lower()
    for wake_word in wake_words:
        wake = wake_word.lower().strip()
        if lower.startswith(wake):
            return text[len(wake) :].lstrip(" ,.:;-!")
    return text


def human_bytes(value: int | float) -> str:
    """Format byte counts for humans."""
    value = float(value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


_RELATIVE_RE = re.compile(
    r"\bin (\d+)\s*(second|seconds|minute|minutes|hour|hours|day|days|week|weeks)\b"
)
_CLOCK_RE = re.compile(r"\bat (\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)?\b")


def parse_delay(text: str, now: datetime | None = None) -> datetime | None:
    """Parse natural-language times into an absolute datetime.

    Understands relative phrases ("in 10 minutes", "in 2 days"), clock times
    ("at 6pm", "at 18:30", "at 6:30 pm"), and "tomorrow" with or without a time.

    A bare hour with no am/pm is read as an evening time when it is 1-7
    ("remind me at 6" means 6pm) and taken literally for 8-23.
    """
    now = now or datetime.now()
    lower = text.lower()

    relative = _RELATIVE_RE.search(lower)
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2)
        if unit.startswith("second"):
            return now + timedelta(seconds=amount)
        if unit.startswith("minute"):
            return now + timedelta(minutes=amount)
        if unit.startswith("hour"):
            return now + timedelta(hours=amount)
        if unit.startswith("day"):
            return now + timedelta(days=amount)
        if unit.startswith("week"):
            return now + timedelta(weeks=amount)
        return None

    clock = _CLOCK_RE.search(lower)
    if clock:
        hour = int(clock.group(1))
        minute = int(clock.group(2) or 0)
        meridiem = (clock.group(3) or "").replace(".", "")
        if meridiem == "pm" and hour < 12:
            hour += 12
        elif meridiem == "am" and hour == 12:
            hour = 0
        elif not meridiem and 1 <= hour <= 7:
            hour += 12
        if hour > 23 or minute > 59:
            return None
        tomorrow = "tomorrow" in lower or "tmrw" in lower
        base = now + timedelta(days=1) if tomorrow else now
        target = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # A time already gone today means the same time tomorrow.
        if not tomorrow and target <= now:
            target += timedelta(days=1)
        return target

    if "tomorrow" in lower or "tmrw" in lower:
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    return None


#: Values that mean "the template text was never replaced".
PLACEHOLDER_PREFIXES = ("your_", "placeholder", "changeme", "xxx", "insert_", "todo")


def is_placeholder_secret(value: str | None) -> bool:
    """True when a credential is missing or still holds the shipped template text.

    Without this, a fresh ``.env`` counts as "configured" and integrations claim
    to be live while every call fails.
    """
    if not value or not value.strip():
        return True
    return value.strip().lower().startswith(PLACEHOLDER_PREFIXES)


def safe_filename(name: str, default: str = "jarvis_file") -> str:
    """Convert arbitrary text into a safe filename stem."""
    stem = re.sub(r"[^a-zA-Z0-9._ -]+", "", name).strip().replace(" ", "_")
    return stem or default


def ensure_directory(path: str | Path) -> Path:
    """Create a directory and return its resolved Path."""
    directory = Path(path).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    return directory

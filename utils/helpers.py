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


def parse_delay(text: str) -> datetime | None:
    """Parse small natural-language delay phrases like 'in 10 minutes'."""
    now = datetime.now()
    match = re.search(r"in (\d+)\s*(second|seconds|minute|minutes|hour|hours|day|days)", text)
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    if unit.startswith("second"):
        return now + timedelta(seconds=amount)
    if unit.startswith("minute"):
        return now + timedelta(minutes=amount)
    if unit.startswith("hour"):
        return now + timedelta(hours=amount)
    if unit.startswith("day"):
        return now + timedelta(days=amount)
    return None


def safe_filename(name: str, default: str = "jarvis_file") -> str:
    """Convert arbitrary text into a safe filename stem."""
    stem = re.sub(r"[^a-zA-Z0-9._ -]+", "", name).strip().replace(" ", "_")
    return stem or default


def ensure_directory(path: str | Path) -> Path:
    """Create a directory and return its resolved Path."""
    directory = Path(path).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    return directory

"""Environment loading helpers for Jarvis V2."""

from __future__ import annotations

import os
from pathlib import Path


def _detect_encoding(data: bytes) -> str:
    """Return the most likely encoding for *data* based on BOM markers.

    Windows Notepad (and some editors) save .env files as UTF-16 with BOM,
    which breaks a plain ``open(..., encoding='utf-8')`` call.  This helper
    inspects the first few bytes so we can decode correctly.
    """
    if data[:4] in (b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff"):
        return "utf-32"
    if data[:2] == b"\xff\xfe":
        return "utf-16-le"
    if data[:2] == b"\xfe\xff":
        return "utf-16-be"
    if data[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    return "utf-8"


def load_env_file(path: str | Path = ".env") -> None:
    """Load a dotenv-style file without requiring python-dotenv.

    Handles UTF-8, UTF-8 with BOM, UTF-16 LE/BE, and UTF-32 — the encodings
    Windows Notepad and common editors may produce.  Existing environment
    variables win.  Values are intentionally never logged.
    """

    env_path = Path(path)
    if not env_path.exists():
        return

    raw_bytes = env_path.read_bytes()
    encoding = _detect_encoding(raw_bytes)
    text = raw_bytes.decode(encoding)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        # Strip any leftover BOM character that survived decoding
        line = line.lstrip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

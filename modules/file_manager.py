"""File and folder commands."""

from __future__ import annotations

import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any

from utils.helpers import ensure_directory, safe_filename


SPECIAL_DIRS = {
    "desktop": Path.home() / "Desktop",
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
    "pictures": Path.home() / "Pictures",
    "home": Path.home(),
}


class FileManager:
    """Open folders, create directories, and find files."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def open_path(self, path: Path) -> str:
        path = path.expanduser()
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
            return f"Opening {path}, sir."
        except Exception:
            return f"I could not open {path}, sir."

    def create_folder(self, name: str, base: str = "desktop") -> str:
        base_path = SPECIAL_DIRS.get(base.lower(), Path.cwd())
        path = base_path / safe_filename(name, "New_Folder")
        path.mkdir(parents=True, exist_ok=True)
        return f"Folder created at {path}, sir."

    def search_files(self, query: str, root: Path | None = None, limit: int = 10) -> str:
        root = root or Path.home()
        matches: list[str] = []
        for current, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if not d.startswith(".")][:20]
            for file in files:
                if query.lower() in file.lower():
                    matches.append(str(Path(current) / file))
                    if len(matches) >= limit:
                        break
            if len(matches) >= limit:
                break
        if not matches:
            return f"I found no files matching {query}, sir."
        return "I found these files: " + "; ".join(matches)

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        for key, path in SPECIAL_DIRS.items():
            if f"open {key}" in lower or f"open my {key}" in lower:
                return {"success": True, "response": self.open_path(path)}
        create_match = re.search(r"create (?:a )?folder(?: called| named)? ([\w ._-]+)", command, re.I)
        if create_match:
            return {"success": True, "response": self.create_folder(create_match.group(1))}
        search_match = re.search(r"(?:find|search for|locate) (?:file )?(.+)", command, re.I)
        if search_match:
            return {"success": True, "response": self.search_files(search_match.group(1).strip())}
        return {"success": False, "response": "I did not find a file command, sir."}

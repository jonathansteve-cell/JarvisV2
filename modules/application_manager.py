"""Application launch and process management."""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore


APP_ALIASES = {
    "chrome": ["chrome", "google-chrome", "chrome.exe"],
    "firefox": ["firefox", "firefox.exe"],
    "edge": ["msedge", "microsoft-edge", "msedge.exe"],
    "vscode": ["code", "Code.exe"],
    "visual studio code": ["code", "Code.exe"],
    "notepad": ["notepad.exe", "notepad"],
    "calculator": ["calc.exe", "gnome-calculator", "kcalc"],
    "spotify": ["spotify", "Spotify.exe"],
    "word": ["winword.exe", "Microsoft Word"],
    "zoom": ["zoom", "Zoom.exe"],
}


class ApplicationManager:
    """Launch, close, and inspect applications."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def _candidate_names(self, app_name: str) -> list[str]:
        key = app_name.lower().strip()
        return APP_ALIASES.get(key, [app_name])

    def open_app(self, app_name: str) -> str:
        app_name = app_name.strip()
        system = platform.system()
        candidates = self._candidate_names(app_name)
        try:
            if system == "Windows":
                for candidate in candidates:
                    if candidate.endswith(".exe") or " " not in candidate:
                        subprocess.Popen(candidate, shell=True)
                        return f"Opening {app_name}, sir."
                os.startfile(app_name)  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                for candidate in candidates:
                    executable = shutil.which(candidate)
                    if executable:
                        subprocess.Popen([executable])
                        return f"Opening {app_name}, sir."
                subprocess.Popen([app_name])
            return f"Opening {app_name}, sir."
        except Exception:
            return f"I could not open {app_name}. Add its executable to PATH or config, sir."

    def close_app(self, app_name: str) -> str:
        app_name = app_name.lower().strip()
        if not psutil:
            return "Process closing requires psutil, sir."
        closed = 0
        for proc in psutil.process_iter(["name"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if app_name in name:
                    proc.terminate()
                    closed += 1
            except Exception:
                continue
        return f"Closed {closed} matching process(es), sir." if closed else f"I found no running {app_name}, sir."

    def list_apps(self) -> str:
        if not psutil:
            return "Process listing requires psutil, sir."
        names = []
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info.get("name")
                if name and name not in names:
                    names.append(name)
            except Exception:
                pass
        names = sorted(names)[:12]
        return "Running applications include: " + ", ".join(names) if names else "No applications detected, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        open_match = re.match(r"(?:open|launch|start|run) (.+)", lower)
        if open_match:
            return {"success": True, "response": self.open_app(open_match.group(1))}
        close_match = re.match(r"(?:close|quit|kill) (.+)", lower)
        if close_match:
            return {"success": True, "response": self.close_app(close_match.group(1))}
        if "what is running" in lower or "running apps" in lower or "list applications" in lower:
            return {"success": True, "response": self.list_apps()}
        return {"success": False, "response": "I did not find an application command, sir."}

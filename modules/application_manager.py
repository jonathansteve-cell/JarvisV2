"""Application launch and process management.

Launch resolution order:
1. ``applications.paths`` in config/config.json (user overrides, wins first)
2. Known per-OS install locations (Program Files, %LOCALAPPDATA%, /Applications, ...)
3. PATH lookup (shutil.which) across known executable aliases
4. Windows ``start`` (resolves the App Paths registry) / macOS ``open -a``

If everything fails, Jarvis explains exactly how to add the app's path to config.
"""

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

# Words people append that are not part of the executable name.
FILLER_WORDS = {"browser", "app", "application", "please", "now", "up", "quickly"}

# Executable-name aliases per app, per lookup style.
APP_ALIASES = {
    "chrome": ["chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
    "google chrome": ["chrome", "google-chrome", "google-chrome-stable"],
    "firefox": ["firefox", "firefox-esr"],
    "edge": ["msedge", "microsoft-edge", "microsoft-edge-stable"],
    "brave": ["brave", "brave-browser"],
    "vscode": ["code"],
    "visual studio code": ["code"],
    "code": ["code"],
    "notepad": ["notepad", "notepad.exe"],
    "notepad++": ["notepad++"],
    "calculator": ["calc", "gnome-calculator", "kcalc"],
    "spotify": ["spotify", "Spotify.exe"],
    "discord": ["discord", "Discord.exe"],
    "whatsapp": ["whatsapp", "WhatsApp.exe"],
    "word": ["winword"],
    "excel": ["excel"],
    "powerpoint": ["powerpnt"],
    "zoom": ["zoom", "Zoom.exe"],
    "vlc": ["vlc"],
    "steam": ["steam", "steam.exe"],
    "obsidian": ["obsidian", "Obsidian.exe"],
    "terminal": ["wt", "gnome-terminal", "konsole", "xterm"],
    "explorer": ["explorer"],
    "files": ["explorer", "nautilus", "finder"],
}

# macOS .app names for `open -a`.
MAC_APP_NAMES = {
    "chrome": ["Google Chrome", "Chromium"],
    "google chrome": ["Google Chrome"],
    "firefox": ["Firefox"],
    "edge": ["Microsoft Edge"],
    "brave": ["Brave Browser"],
    "vscode": ["Visual Studio Code"],
    "visual studio code": ["Visual Studio Code"],
    "code": ["Visual Studio Code"],
    "notepad": ["TextEdit"],
    "calculator": ["Calculator"],
    "spotify": ["Spotify"],
    "discord": ["Discord"],
    "whatsapp": ["WhatsApp"],
    "word": ["Microsoft Word"],
    "excel": ["Microsoft Excel"],
    "powerpoint": ["Microsoft PowerPoint"],
    "zoom": ["Zoom"],
    "vlc": ["VLC"],
    "steam": ["Steam"],
    "obsidian": ["Obsidian"],
    "files": ["Finder"],
}

# Known Windows install locations (forward slashes work in all Python APIs).
KNOWN_WINDOWS_PATHS = {
    "chrome": [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "~/AppData/Local/Google/Chrome/Application/chrome.exe",
    ],
    "google chrome": [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "~/AppData/Local/Google/Chrome/Application/chrome.exe",
    ],
    "edge": [
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    ],
    "firefox": [
        "C:/Program Files/Mozilla Firefox/firefox.exe",
        "C:/Program Files (x86)/Mozilla Firefox/firefox.exe",
    ],
    "brave": [
        "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
        "~/AppData/Local/BraveSoftware/Brave-Browser/Application/brave.exe",
    ],
    "vscode": [
        "~/AppData/Local/Programs/Microsoft VS Code/Code.exe",
        "C:/Program Files/Microsoft VS Code/Code.exe",
    ],
    "visual studio code": [
        "~/AppData/Local/Programs/Microsoft VS Code/Code.exe",
        "C:/Program Files/Microsoft VS Code/Code.exe",
    ],
    "code": [
        "~/AppData/Local/Programs/Microsoft VS Code/Code.exe",
        "C:/Program Files/Microsoft VS Code/Code.exe",
    ],
    "notepad": ["C:/Windows/System32/notepad.exe", "C:/Windows/notepad.exe"],
    "notepad++": ["C:/Program Files/Notepad++/notepad++.exe", "C:/Program Files (x86)/Notepad++/notepad++.exe"],
    "calculator": ["C:/Windows/System32/calc.exe"],
    "spotify": ["~/AppData/Roaming/Spotify/Spotify.exe"],
    "discord": ["~/AppData/Local/Discord/Update.exe"],
    "whatsapp": ["~/AppData/Local/WhatsApp/WhatsApp.exe"],
    "word": [
        "C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE",
        "C:/Program Files (x86)/Microsoft Office/root/Office16/WINWORD.EXE",
    ],
    "excel": [
        "C:/Program Files/Microsoft Office/root/Office16/EXCEL.EXE",
        "C:/Program Files (x86)/Microsoft Office/root/Office16/EXCEL.EXE",
    ],
    "powerpoint": [
        "C:/Program Files/Microsoft Office/root/Office16/POWERPNT.EXE",
        "C:/Program Files (x86)/Microsoft Office/root/Office16/POWERPNT.EXE",
    ],
    "zoom": ["~/AppData/Roaming/Zoom/bin/Zoom.exe"],
    "vlc": ["C:/Program Files/VideoLAN/VLC/vlc.exe"],
    "steam": ["C:/Program Files (x86)/Steam/steam.exe"],
    "obsidian": ["~/AppData/Local/Obsidian/Obsidian.exe"],
}


def _clean_app_name(raw: str) -> str:
    """Strip filler words: 'chrome browser please' -> 'chrome'."""
    words = raw.strip().split()
    while words and words[-1].lower() in FILLER_WORDS:
        words.pop()
    return " ".join(words) if words else raw.strip()


def _existing(paths: list[str]) -> Path | None:
    for entry in paths:
        path = Path(os.path.expandvars(str(Path(entry).expanduser())))
        if path.is_file():
            return path
    return None


class ApplicationManager:
    """Launch, close, and inspect applications."""

    def __init__(self, config: Any) -> None:
        self.config = config

    # ------------------------------------------------------------ resolution
    def _config_path(self, key: str) -> Path | None:
        """User-configured absolute paths win over everything (applications.paths)."""
        mapping = self.config.get("applications.paths", {}) or {}
        value = mapping.get(key.lower()) or mapping.get(Path(key).stem.lower())
        if not value:
            return None
        path = Path(os.path.expandvars(str(Path(str(value)).expanduser())))
        return path if path.is_file() else None

    def _candidates(self, app_name: str) -> list[str]:
        key = app_name.lower().strip()
        aliases = APP_ALIASES.get(key, [])
        names = list(dict.fromkeys([key, *aliases]))
        if platform.system() == "Windows":
            names += [f"{name}.exe" for name in list(names)]
        return names

    def _launch(self, path_or_cmd: list[str] | str) -> None:
        if isinstance(path_or_cmd, str):
            subprocess.Popen(path_or_cmd, shell=True)
        else:
            subprocess.Popen(path_or_cmd)

    def open_app(self, app_name: str) -> str:
        raw = app_name.strip()
        app_name = _clean_app_name(raw)
        key = app_name.lower()
        system = platform.system()

        # 1) Explicit config paths.
        configured = self._config_path(key)
        if configured:
            try:
                if system == "Windows":
                    os.startfile(str(configured))  # type: ignore[attr-defined]
                else:
                    self._launch([str(configured)])
                return f"Opening {app_name}, sir."
            except Exception:
                pass

        # 2) Known install locations.
        known = _existing(KNOWN_WINDOWS_PATHS.get(key, [])) if system == "Windows" else None
        if known:
            try:
                os.startfile(str(known))  # type: ignore[attr-defined]
                return f"Opening {app_name}, sir."
            except Exception:
                pass

        # 3) PATH lookup across aliases.
        for candidate in self._candidates(app_name):
            executable = shutil.which(candidate)
            if executable:
                try:
                    self._launch([executable])
                    return f"Opening {app_name}, sir."
                except Exception:
                    continue

        # 4) Platform launchers.
        try:
            if system == "Windows":
                # `start` resolves the App Paths registry (Chrome, Edge, etc.).
                base = Path(app_name).stem if app_name.lower().endswith(".exe") else app_name
                subprocess.Popen(f'start "" "{base}"', shell=True)
                return f"Opening {app_name}, sir."
            if system == "Darwin":
                for name in MAC_APP_NAMES.get(key, [app_name.title()]):
                    result = subprocess.run(
                        ["open", "-a", name], capture_output=True, check=False
                    )
                    if result.returncode == 0:
                        return f"Opening {app_name}, sir."
                raise FileNotFoundError(app_name)
            self._launch([app_name])
            return f"Opening {app_name}, sir."
        except Exception:
            pass

        return (
            f"I could not find a way to launch {app_name}, sir. Add its full executable "
            f"under 'applications.paths' in config/config.json — for example: "
            f"\"{key}\": \"C:/Program Files/Google/{key}/{key}.exe\""
        )

    # ------------------------------------------------------------- processes
    def close_app(self, app_name: str) -> str:
        app_name = _clean_app_name(app_name.lower())
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

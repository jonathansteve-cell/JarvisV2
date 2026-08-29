"""Application launch and process management.

Launch resolution order:
1. ``applications.paths`` in config/config.json (user overrides, wins first)
2. Known per-OS install locations (Program Files, %LOCALAPPDATA%, /Applications, ...)
3. PATH lookup (shutil.which) across known executable aliases
4. Anything the OS knows about, by fuzzy name:
   * Windows - App Paths registry keys and Start Menu ``.lnk`` shortcuts
   * macOS   - ``/Applications`` + Spotlight
   * Linux   - ``.desktop`` entries in the XDG data dirs
5. A bounded scan of the usual install roots for ``<name>*.exe``
6. Windows ``start`` / macOS ``open -a`` as a last resort

If everything fails, Jarvis explains exactly how to add the app's path to config
and lists where it looked.
"""

from __future__ import annotations

import difflib
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
FILLER_WORDS = {
    "browser",
    "app",
    "application",
    "program",
    "software",
    "please",
    "now",
    "up",
    "quickly",
    "me",
    "for",
    "kindly",
}

# Words people prepend that are not part of the executable name.
LEADING_FILLER = {"the", "a", "an", "up", "please", "for", "me", "my", "open", "launch", "start", "run", "kindly"}

# Executable-name aliases per app, per lookup style.
APP_ALIASES = {
    "chrome": ["chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
    "google chrome": ["chrome", "google-chrome", "google-chrome-stable"],
    "firefox": ["firefox", "firefox-esr"],
    "edge": ["msedge", "microsoft-edge", "microsoft-edge-stable"],
    "microsoft edge": ["msedge", "microsoft-edge"],
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
    "telegram": ["telegram", "Telegram.exe"],
    "slack": ["slack", "Slack.exe"],
    "teams": ["ms-teams", "Teams.exe", "msteams"],
    "microsoft teams": ["ms-teams", "Teams.exe"],
    "word": ["winword"],
    "excel": ["excel"],
    "powerpoint": ["powerpnt"],
    "outlook": ["outlook"],
    "onenote": ["onenote"],
    "zoom": ["zoom", "Zoom.exe"],
    "vlc": ["vlc"],
    "steam": ["steam", "steam.exe"],
    "obsidian": ["obsidian", "Obsidian.exe"],
    "blender": ["blender"],
    "gimp": ["gimp"],
    "photoshop": ["Photoshop.exe"],
    "sublime": ["sublime_text", "subl"],
    "sublime text": ["sublime_text", "subl"],
    "pycharm": ["pycharm64", "pycharm"],
    "android studio": ["studio64", "studio"],
    "intellij": ["idea64", "idea"],
    "terminal": ["wt", "gnome-terminal", "konsole", "xterm"],
    "windows terminal": ["wt"],
    "command prompt": ["cmd"],
    "cmd": ["cmd"],
    "powershell": ["powershell", "pwsh"],
    "task manager": ["taskmgr"],
    "control panel": ["control"],
    "settings": ["ms-settings:", "gnome-control-center"],
    "paint": ["mspaint"],
    "snipping tool": ["SnippingTool.exe"],
    "media player": ["wmplayer"],
    "photos": ["ms-photos:"],
    "camera": ["microsoft.windows.camera:"],
    "explorer": ["explorer"],
    "files": ["explorer", "nautilus", "finder"],
    "file explorer": ["explorer", "nautilus", "dolphin", "thunar", "finder"],
    "windows explorer": ["explorer"],
}

# macOS .app names for `open -a`.
MAC_APP_NAMES = {
    "chrome": ["Google Chrome", "Chromium"],
    "google chrome": ["Google Chrome"],
    "firefox": ["Firefox"],
    "edge": ["Microsoft Edge"],
    "microsoft edge": ["Microsoft Edge"],
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
    "outlook": ["Microsoft Outlook"],
    "onenote": ["Microsoft OneNote"],
    "zoom": ["Zoom"],
    "vlc": ["VLC"],
    "steam": ["Steam"],
    "obsidian": ["Obsidian"],
    "blender": ["Blender"],
    "photoshop": ["Adobe Photoshop"],
    "files": ["Finder"],
    "file explorer": ["Finder"],
    "terminal": ["Terminal"],
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
    "microsoft edge": [
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
    "telegram": ["~/AppData/Roaming/Telegram Desktop/Telegram.exe"],
    "slack": ["~/AppData/Local/slack/slack.exe"],
    "teams": ["~/AppData/Local/Microsoft/Teams/current/Teams.exe"],
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
    "outlook": [
        "C:/Program Files/Microsoft Office/root/Office16/OUTLOOK.EXE",
        "C:/Program Files (x86)/Microsoft Office/root/Office16/OUTLOOK.EXE",
    ],
    "zoom": ["~/AppData/Roaming/Zoom/bin/Zoom.exe"],
    "vlc": ["C:/Program Files/VideoLAN/VLC/vlc.exe"],
    "steam": ["C:/Program Files (x86)/Steam/steam.exe"],
    "obsidian": ["~/AppData/Local/Obsidian/Obsidian.exe"],
    "blender": [
        "C:/Program Files/Blender Foundation/Blender 4.2/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 4.1/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 3.6/blender.exe",
    ],
    "gimp": ["C:/Program Files/GIMP 2/bin/gimp-2.10.exe"],
    "sublime": ["C:/Program Files/Sublime Text/sublime_text.exe"],
    "sublime text": ["C:/Program Files/Sublime Text/sublime_text.exe"],
    "pycharm": ["~/AppData/Local/JetBrains/Toolbox/apps/pycharm/bin/pycharm64.exe"],
    "paint": ["C:/Windows/System32/mspaint.exe"],
    "task manager": ["C:/Windows/System32/taskmgr.exe"],
    "command prompt": ["C:/Windows/System32/cmd.exe"],
    "cmd": ["C:/Windows/System32/cmd.exe"],
    "powershell": [
        "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        "C:/Program Files/PowerShell/7/pwsh.exe",
    ],
    "file explorer": ["C:/Windows/explorer.exe"],
    "windows explorer": ["C:/Windows/explorer.exe"],
    "explorer": ["C:/Windows/explorer.exe"],
}

#: Roots scanned on Windows when an app is not in any known location.
WINDOWS_INSTALL_ROOTS = [
    "C:/Program Files",
    "C:/Program Files (x86)",
    "~/AppData/Local",
    "~/AppData/Local/Programs",
    "~/AppData/Roaming",
]

#: How many directory entries a broad install-root scan will look at.
SCAN_BUDGET = 4000


def _normalize(name: str) -> str:
    """Lowercase and drop punctuation so 'Notepad++' matches 'notepad'."""
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def _clean_app_name(raw: str) -> str:
    """Strip filler words: 'up the chrome browser please' -> 'chrome'."""
    words = raw.strip().strip("'\"").split()
    while words and words[-1].lower() in FILLER_WORDS:
        words.pop()
    while words and words[0].lower() in LEADING_FILLER:
        words.pop(0)
    return " ".join(words) if words else raw.strip()


def _fuzzy_best(target: str, options: list[str], cutoff: float = 0.82) -> str | None:
    """Closest option to ``target`` on normalized text, or None."""
    if not options:
        return None
    normalized_target = _normalize(target)
    normalized_options = {_normalize(option): option for option in options}
    if normalized_target in normalized_options:
        return normalized_options[normalized_target]
    matches = difflib.get_close_matches(normalized_target, list(normalized_options), n=1, cutoff=cutoff)
    return normalized_options[matches[0]] if matches else None


def _existing(paths: list[str]) -> Path | None:
    for entry in paths:
        path = Path(os.path.expandvars(str(Path(entry).expanduser())))
        if path.is_file():
            return path
    return None


def start_menu_dirs() -> list[Path]:
    """Start Menu folders that hold the shortcuts Windows shows to users."""
    if platform.system() != "Windows":
        return []
    roots = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
    ]
    return [Path(root) for root in roots if root and Path(root).is_dir()]


def _start_menu_shortcut(app_name: str) -> Path | None:
    """Find a Start Menu ``.lnk`` whose name matches the app (fuzzy)."""
    names: list[str] = []
    index: dict[str, Path] = {}
    for root in start_menu_dirs():
        try:
            for shortcut in root.rglob("*.lnk"):
                stem = shortcut.stem
                names.append(stem)
                index.setdefault(_normalize(stem), shortcut)
        except Exception:
            continue
    match = _fuzzy_best(app_name, names)
    return index.get(_normalize(match)) if match else None


def _app_paths_registry(app_name: str) -> Path | None:
    """Read the Windows App Paths registry, which is how ``start`` finds apps."""
    if platform.system() != "Windows":
        return None
    try:
        import winreg  # type: ignore
    except Exception:
        return None

    subkeys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
    ]
    candidates = [app_name, f"{app_name}.exe"]
    candidates += [f"{alias}.exe" for alias in APP_ALIASES.get(app_name.lower(), [])]

    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for subkey in subkeys:
            for candidate in candidates:
                try:
                    with winreg.OpenKey(hive, f"{subkey}\\{candidate}") as key:
                        value, _ = winreg.QueryValueEx(key, "")
                        path = Path(os.path.expandvars(str(value)))
                        if path.is_file():
                            return path
                except OSError:
                    continue

    # Fall back to a fuzzy scan of the registered executable names.
    registered: list[str] = []
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for subkey in subkeys:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    count = winreg.QueryInfoKey(key)[0]
                    registered.extend(winreg.EnumKey(key, i) for i in range(count))
            except OSError:
                continue
    match = _fuzzy_best(app_name, registered, cutoff=0.86)
    if not match:
        return None
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for subkey in subkeys:
            try:
                with winreg.OpenKey(hive, f"{subkey}\\{match}") as key:
                    value, _ = winreg.QueryValueEx(key, "")
                    path = Path(os.path.expandvars(str(value)))
                    if path.is_file():
                        return path
            except OSError:
                continue
    return None


def _scan_install_roots(app_name: str) -> Path | None:
    """Bounded search of common install roots for ``<name>*.exe``."""
    if platform.system() != "Windows":
        return None
    stem = _normalize(app_name) or _normalize(Path(app_name).stem)
    if not stem:
        return None
    seen = 0
    for root_text in WINDOWS_INSTALL_ROOTS:
        root = Path(os.path.expandvars(str(Path(root_text).expanduser())))
        if not root.is_dir():
            continue
        try:
            entries = list(root.iterdir())
        except Exception:
            continue
        for entry in entries:
            seen += 1
            if seen > SCAN_BUDGET:
                return None
            if not entry.is_dir() or stem not in _normalize(entry.name):
                continue
            try:
                for exe in entry.rglob(f"{Path(app_name).stem}*.exe"):
                    if exe.is_file():
                        return exe
            except Exception:
                continue
    return None


def desktop_entry_dirs() -> list[Path]:
    """XDG folders that hold ``.desktop`` launchers on Linux."""
    if platform.system() == "Windows":
        return []
    candidates = [Path.home() / ".local" / "share" / "applications"]
    for chunk in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(os.pathsep):
        if chunk:
            candidates.append(Path(chunk) / "applications")
    candidates += [Path("/usr/share/applications"), Path("/usr/local/share/applications")]
    unique: list[Path] = []
    for path in candidates:
        if path.is_dir() and path not in unique:
            unique.append(path)
    return unique


def _desktop_entry(app_name: str) -> Path | None:
    """Find the ``.desktop`` launcher whose name matches the app (fuzzy)."""
    names: list[str] = []
    index: dict[str, Path] = {}
    for folder in desktop_entry_dirs():
        try:
            for entry in folder.glob("*.desktop"):
                names.append(entry.stem)
                index.setdefault(_normalize(entry.stem), entry)
        except Exception:
            continue
    match = _fuzzy_best(app_name, names)
    return index.get(_normalize(match)) if match else None


def _mac_app_bundle(app_name: str) -> str | None:
    """Find an installed ``.app`` bundle by fuzzy name on macOS."""
    bundles: list[str] = []
    for root in (Path("/Applications"), Path.home() / "Applications"):
        if not root.is_dir():
            continue
        try:
            bundles.extend(path.stem for path in root.glob("*.app"))
        except Exception:
            continue
    return _fuzzy_best(app_name, bundles)


class ApplicationManager:
    """Launch, close, and inspect applications."""

    def __init__(self, config: Any) -> None:
        self.config = config

    # ------------------------------------------------------------ resolution
    def clean_target(self, raw: str) -> str:
        """Public wrapper around the filler-word cleaner."""
        return _clean_app_name(raw)

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

    def _start(self, configured: Path) -> bool:
        """Open a resolved executable/bundle the OS-native way."""
        try:
            if platform.system() == "Windows":
                os.startfile(str(configured))  # type: ignore[attr-defined]
            else:
                self._launch([str(configured)])
            return True
        except Exception:
            return False

    def _discovered_target(self, app_name: str, key: str) -> tuple[Path | None, str]:
        """Ask the operating system where this app lives. Returns (path, method)."""
        system = platform.system()
        if system == "Windows":
            registry = _app_paths_registry(key)
            if registry:
                return registry, "App Paths registry"
            shortcut = _start_menu_shortcut(key)
            if shortcut:
                return shortcut, "Start Menu shortcut"
            scanned = _scan_install_roots(key)
            if scanned:
                return scanned, "install-folder scan"
        elif system == "Darwin":
            bundle = _mac_app_bundle(key)
            if bundle:
                for root in (Path("/Applications"), Path.home() / "Applications"):
                    candidate = root / f"{bundle}.app"
                    if candidate.exists():
                        return candidate, "Applications folder"
        else:
            entry = _desktop_entry(key)
            if entry:
                return entry, "desktop entry"
        return None, "none"

    def open_app(self, app_name: str) -> str:
        """Resolve and launch an app; returns a spoken-style message."""
        return self.try_open(app_name)[1]

    def try_open(self, app_name: str) -> tuple[bool, str]:
        """Resolve and launch an app. Returns ``(launched, message)``."""
        raw = app_name.strip()
        app_name = _clean_app_name(raw)
        key = app_name.lower()
        system = platform.system()

        # 1) Explicit config paths.
        configured = self._config_path(key)
        if configured and self._start(configured):
            return True, f"Opening {app_name}, sir."

        # 2) Known install locations.
        known = _existing(KNOWN_WINDOWS_PATHS.get(key, [])) if system == "Windows" else None
        if known and self._start(known):
            return True, f"Opening {app_name}, sir."

        # 3) PATH lookup across aliases.
        for candidate in self._candidates(app_name):
            executable = shutil.which(candidate)
            if executable:
                try:
                    self._launch([executable])
                    return True, f"Opening {app_name}, sir."
                except Exception:
                    continue

        # 4) Whatever the OS knows about, matched by fuzzy name.
        discovered, method = self._discovered_target(app_name, key)
        if discovered:
            if system == "Linux" and discovered.suffix == ".desktop":
                result = subprocess.run(
                    ["gio", "launch", str(discovered)], capture_output=True, check=False
                )
                if result.returncode == 0:
                    return True, f"Opening {app_name}, sir."
            elif self._start(discovered):
                return True, f"Opening {app_name}, sir."
            else:
                return True, f"Found {app_name} via {method} but it would not start, sir."

        # 5) Platform launchers.
        try:
            if system == "Windows":
                # `start` resolves the App Paths registry (Chrome, Edge, ...).
                base = Path(app_name).stem if app_name.lower().endswith(".exe") else app_name
                subprocess.Popen(f'start "" "{base}"', shell=True)
                return True, f"Opening {app_name}, sir."
            if system == "Darwin":
                for name in MAC_APP_NAMES.get(key, [app_name.title()]):
                    result = subprocess.run(
                        ["open", "-a", name], capture_output=True, check=False
                    )
                    if result.returncode == 0:
                        return True, f"Opening {app_name}, sir."
                raise FileNotFoundError(app_name)
            self._launch([app_name])
            return True, f"Opening {app_name}, sir."
        except Exception:
            pass

        searched = [
            "applications.paths in config/config.json",
            "known install folders",
            "the system PATH",
            "the operating system app registry",
        ]
        return False, (
            f"I could not find a way to launch {app_name}, sir. I checked "
            f"{', '.join(searched)}. Add its full executable "
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
            target = _clean_app_name(open_match.group(1))
            launched, message = self.try_open(open_match.group(1))
            return {
                "success": True,
                "response": message,
                "data": {"launched": launched, "app": target},
            }
        close_match = re.match(r"(?:close|quit|kill) (.+)", lower)
        if close_match:
            return {"success": True, "response": self.close_app(close_match.group(1))}
        if "what is running" in lower or "running apps" in lower or "list applications" in lower:
            return {"success": True, "response": self.list_apps()}
        return {"success": False, "response": "I did not find an application command, sir."}

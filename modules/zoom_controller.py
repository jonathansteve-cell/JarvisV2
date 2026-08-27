"""Zoom meeting controls."""

from __future__ import annotations

import re
import urllib.parse
import webbrowser
from typing import Any


class ZoomController:
    """Join Zoom meetings and send common Zoom hotkeys."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def join(self, meeting_id: str, password: str = "") -> str:
        meeting_id = re.sub(r"\D", "", meeting_id)
        if not meeting_id:
            return "I need a Zoom meeting ID, sir."
        url = f"zoommtg://zoom.us/join?confno={meeting_id}"
        if password:
            url += "&pwd=" + urllib.parse.quote(password)
        webbrowser.open(url)
        return f"Joining Zoom meeting {meeting_id}, sir."

    def hotkey(self, action: str) -> str:
        try:
            import pyautogui  # type: ignore

            if action == "mute":
                pyautogui.hotkey("alt", "a")
                return "Zoom mute toggled, sir."
            if action == "video":
                pyautogui.hotkey("alt", "v")
                return "Zoom video toggled, sir."
        except Exception:
            pass
        return "Zoom hotkeys are unavailable on this machine, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        if "zoom" not in lower and "meeting" not in lower:
            return {"success": False, "response": "I did not find a Zoom command, sir."}
        match = re.search(r"join (?:zoom )?(?:meeting )?(\d[\d -]+)(?: password (\S+))?", command, re.I)
        if match:
            return {"success": True, "response": self.join(match.group(1), match.group(2) or "")}
        if "mute" in lower:
            return {"success": True, "response": self.hotkey("mute")}
        if "video" in lower:
            return {"success": True, "response": self.hotkey("video")}
        return {"success": False, "response": "I did not find a Zoom command, sir."}

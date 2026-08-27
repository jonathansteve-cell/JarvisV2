"""Window control via pyautogui hotkeys."""

from __future__ import annotations

import platform
from typing import Any


class WindowManager:
    """Window positioning operations using standard OS hotkeys."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def _hotkey(self, *keys: str) -> bool:
        try:
            import pyautogui  # type: ignore

            pyautogui.hotkey(*keys)
            return True
        except Exception:
            return False

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        system = platform.system()
        if "maximize" in lower:
            ok = self._hotkey("win", "up") if system == "Windows" else self._hotkey("alt", "space")
            return {"success": ok, "response": "Maximizing the active window, sir." if ok else "Window automation is unavailable, sir."}
        if "minimize" in lower:
            ok = self._hotkey("win", "down") if system == "Windows" else self._hotkey("command", "m")
            return {"success": ok, "response": "Minimizing the active window, sir." if ok else "Window automation is unavailable, sir."}
        if "left" in lower and ("tile" in lower or "snap" in lower or "window" in lower):
            ok = self._hotkey("win", "left") if system == "Windows" else False
            return {"success": ok, "response": "Snapping left, sir." if ok else "Left snap is not available on this host, sir."}
        if "right" in lower and ("tile" in lower or "snap" in lower or "window" in lower):
            ok = self._hotkey("win", "right") if system == "Windows" else False
            return {"success": ok, "response": "Snapping right, sir." if ok else "Right snap is not available on this host, sir."}
        if "close window" in lower:
            ok = self._hotkey("alt", "f4") if system == "Windows" else self._hotkey("command", "w")
            return {"success": ok, "response": "Closing the active window, sir." if ok else "Window close hotkey is unavailable, sir."}
        return {"success": False, "response": "I did not find a window command, sir."}

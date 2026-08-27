"""Screenshot operations."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from utils.helpers import ensure_directory


class ScreenshotManager:
    """Capture screenshots using pyautogui or Pillow."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.directory = ensure_directory(config.get("paths.screenshot_dir", "screenshots"))

    def take_screenshot(self, name: str | None = None) -> str:
        filename = name or f"jarvis_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = self.directory / filename
        try:
            import pyautogui  # type: ignore

            image = pyautogui.screenshot()
            image.save(path)
            return f"Screenshot captured and saved to {path}, sir."
        except Exception:
            try:
                from PIL import ImageGrab  # type: ignore

                image = ImageGrab.grab()
                image.save(path)
                return f"Screenshot captured and saved to {path}, sir."
            except Exception:
                return "I could not capture a screenshot on this machine, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        if "screenshot" in lower or "screen shot" in lower or "capture screen" in lower:
            return {"success": True, "response": self.take_screenshot()}
        return {"success": False, "response": "I did not find a screenshot command, sir."}

"""Simple command chaining and named routines."""

from __future__ import annotations

from typing import Any, Callable


class AutomationController:
    """Run routines by delegating back to Jarvis command processing."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.routines: dict[str, list[str]] = {
            "morning routine": ["system status", "open calendar", "weather"],
            "work mode": ["open chrome", "open visual studio code", "volume 35"],
            "meeting mode": ["volume 50", "open zoom"],
            "focus mode": ["mute audio", "open spotify"],
        }

    def split_chain(self, command: str) -> list[str]:
        separators = [" then ", " and then ", ";"]
        parts = [command]
        for separator in separators:
            next_parts: list[str] = []
            for part in parts:
                next_parts.extend(part.split(separator))
            parts = next_parts
        return [part.strip() for part in parts if part.strip()]

    def process_routine(self, command: str, runner: Callable[[str], Any]) -> dict[str, Any]:
        lower = command.lower()
        for name, commands in self.routines.items():
            if name in lower or f"run {name}" in lower:
                responses = []
                for item in commands:
                    result = runner(item)
                    responses.append(getattr(result, "text", str(result)))
                return {"success": True, "response": f"{name.title()} complete. " + " ".join(responses)}
        return {"success": False, "response": "I did not find an automation routine, sir."}

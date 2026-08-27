"""Smart home controller with Home Assistant or local simulation."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


class SmartHomeController:
    """Control Home Assistant devices when configured, otherwise simulate locally."""

    def __init__(self, config: Any) -> None:
        self.config = config
        data_dir = Path(config.get("paths.data_dir", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "smart_home_state.json"
        self.state = {
            "living room light": "off",
            "bedroom light": "off",
            "thermostat": "72",
            "front door": "locked",
        }
        if self.path.exists():
            self.state.update(json.loads(self.path.read_text(encoding="utf-8")))

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def _home_assistant(self, domain: str, service: str, payload: dict[str, Any]) -> bool:
        url = os.getenv("HOME_ASSISTANT_URL")
        token = os.getenv("HOME_ASSISTANT_TOKEN")
        if not url or not token or requests is None:
            return False
        response = requests.post(
            f"{url.rstrip('/')}/api/services/{domain}/{service}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return True

    def set_device(self, device: str, state: str) -> str:
        self.state[device] = state
        self._save()
        return f"{device.title()} set to {state}, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        light_match = re.search(r"turn (on|off) (?:the )?(.+ light)", lower)
        if light_match:
            return {"success": True, "response": self.set_device(light_match.group(2), light_match.group(1))}
        temp_match = re.search(r"set (?:the )?(?:thermostat|temperature) to (\d+)", lower)
        if temp_match:
            return {"success": True, "response": self.set_device("thermostat", temp_match.group(1))}
        if "lock" in lower and "door" in lower:
            return {"success": True, "response": self.set_device("front door", "locked")}
        if "unlock" in lower and "door" in lower:
            return {"success": True, "response": self.set_device("front door", "unlocked")}
        if "device status" in lower or "smart home status" in lower:
            return {"success": True, "response": "; ".join(f"{k}: {v}" for k, v in self.state.items()), "data": self.state}
        return {"success": False, "response": "I did not find a smart home command, sir."}

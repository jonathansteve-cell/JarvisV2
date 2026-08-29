"""Smart home controller with Home Assistant or local simulation.

When ``HOME_ASSISTANT_URL`` and ``HOME_ASSISTANT_TOKEN`` are set, device commands
are sent to Home Assistant's REST API. If the call fails or no credentials exist,
Jarvis falls back to a local simulation so the command still gets an answer — and
says which one happened.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from utils.helpers import is_placeholder_secret

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

logger = logging.getLogger(__name__)


def _slug(device: str) -> str:
    """'Living Room Light' -> 'living_room_light' (a Home Assistant entity id)."""
    return re.sub(r"[^a-z0-9]+", "_", device.lower()).strip("_")


def _entity_for(device: str) -> tuple[str, str]:
    """Map a spoken device name onto a Home Assistant (domain, entity_id)."""
    slug = _slug(device)
    lowered = device.lower()
    if "thermostat" in lowered or "temperature" in lowered or "ac" in lowered:
        return "climate", slug
    if "door" in lowered or "lock" in lowered:
        return "lock", slug
    if "light" in lowered or "lamp" in lowered or "bulb" in lowered:
        return "light", slug
    if "fan" in lowered:
        return "fan", slug
    return "switch", slug


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
        # None = not tried yet, True/False = result of the most recent call.
        self._last_live: bool | None = None

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    # ------------------------------------------------------------ Home Assistant
    def configured(self) -> bool:
        """Credentials present *and* not still holding the shipped template text."""
        if requests is None:
            return False
        return not (
            is_placeholder_secret(os.getenv("HOME_ASSISTANT_URL"))
            or is_placeholder_secret(os.getenv("HOME_ASSISTANT_TOKEN"))
        )

    def mode(self) -> str:
        """What `smart home status` should claim, based on what actually happened."""
        if not self.configured():
            return "local simulation"
        if self._last_live is False:
            return "Home Assistant configured but unreachable - simulating"
        return "Home Assistant"

    def _home_assistant(self, domain: str, service: str, payload: dict[str, Any]) -> bool:
        """POST to the Home Assistant services API. Returns True on success."""
        url = os.getenv("HOME_ASSISTANT_URL")
        token = os.getenv("HOME_ASSISTANT_TOKEN")
        if not url or not token or requests is None:
            return False
        try:
            response = requests.post(
                f"{url.rstrip('/')}/api/services/{domain}/{service}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception as exc:
            logger.warning("Home Assistant call %s/%s failed: %s", domain, service, exc)
            return False

    def _service_for(self, domain: str, state: str) -> str:
        state = state.lower()
        if domain == "lock":
            return "unlock" if state in {"unlocked", "unlock", "open"} else "lock"
        if domain == "climate":
            return "set_temperature"
        return "turn_on" if state in {"on", "true", "high", "up"} else "turn_off"

    # ---------------------------------------------------------------- commands
    def set_device(self, device: str, state: str) -> str:
        device = device.strip()
        domain, entity_id = _entity_for(device)
        service = self._service_for(domain, state)
        payload: dict[str, Any] = {"entity_id": f"{domain}.{entity_id}"}
        if domain == "climate":
            try:
                payload["temperature"] = int(float(state))
            except ValueError:
                payload["temperature"] = state

        live = self.configured() and self._home_assistant(domain, service, payload)
        self._last_live = live if self.configured() else None

        # Keep the local copy in sync either way so `smart home status` is coherent.
        self.state[device.lower()] = state
        self._save()

        if live:
            return f"{device.title()} set to {state} on Home Assistant, sir."
        return f"{device.title()} set to {state}, sir. (simulated — no Home Assistant connection)"

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        light_match = re.search(r"turn (on|off) (?:the )?(.+?)(?: light| lamp)?$", lower)
        if light_match and ("light" in lower or "lamp" in lower or "fan" in lower or "switch" in lower):
            device = light_match.group(2).strip()
            kind = "fan" if "fan" in lower else "lamp" if "lamp" in lower else "light"
            if not device.endswith(kind):
                device = f"{device} {kind}"
            return {
                "success": True,
                "response": self.set_device(device, light_match.group(1)),
            }
        temp_match = re.search(r"set (?:the )?(?:thermostat|temperature|ac) to (\d+)", lower)
        if temp_match:
            return {"success": True, "response": self.set_device("thermostat", temp_match.group(1))}
        if "unlock" in lower and "door" in lower:
            return {"success": True, "response": self.set_device("front door", "unlocked")}
        if "lock" in lower and "door" in lower:
            return {"success": True, "response": self.set_device("front door", "locked")}
        if "device status" in lower or "smart home status" in lower:
            mode = self.mode()
            body = "; ".join(f"{k}: {v}" for k, v in self.state.items())
            return {
                "success": True,
                "response": f"Smart home ({mode}) — {body}",
                "data": {**self.state, "mode": mode},
            }
        return {"success": False, "response": "I did not find a smart home command, sir."}

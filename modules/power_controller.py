"""Power and Wake-on-LAN helpers."""

from __future__ import annotations

import re
import socket
from typing import Any


class PowerController:
    """Wake sleeping PCs with Wake-on-LAN.

    A fully powered-off PC cannot be turned on by normal desktop software. Wake-on-LAN requires
    BIOS/UEFI support, a network adapter that remains powered, and the target MAC address.
    """

    def __init__(self, config: Any) -> None:
        self.config = config

    def send_wol(self, mac_address: str | None = None, broadcast: str | None = None, port: int | None = None) -> str:
        mac = (mac_address or self.config.get("integrations.wake_on_lan.mac_address", "")).replace("-", ":")
        if not re.fullmatch(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", mac):
            return "Wake-on-LAN needs a valid target MAC address in configuration, sir."
        mac_bytes = bytes.fromhex(mac.replace(":", ""))
        packet = b"\xff" * 6 + mac_bytes * 16
        target = broadcast or self.config.get("integrations.wake_on_lan.broadcast", "255.255.255.255")
        target_port = int(port or self.config.get("integrations.wake_on_lan.port", 9))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(packet, (target, target_port))
        return "Wake-on-LAN magic packet sent, sir. If the PC is configured for WOL, it should wake."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        if "turn on" in lower and ("pc" in lower or "computer" in lower):
            return {
                "success": False,
                "response": (
                    "I cannot turn on a fully powered-off PC by software alone. I can wake a sleeping "
                    "PC with Wake-on-LAN if you configure its MAC address."
                ),
            }
        if "wake" in lower and ("pc" in lower or "computer" in lower):
            return {"success": True, "response": self.send_wol()}
        return {"success": False, "response": "I did not find a power command, sir."}

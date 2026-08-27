"""WhatsApp messaging through Twilio or WhatsApp Web fallback."""

from __future__ import annotations

import os
import re
import urllib.parse
import webbrowser
from typing import Any


class WhatsAppController:
    """Send WhatsApp messages when Twilio is configured, otherwise open WhatsApp Web."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def _twilio_configured(self) -> bool:
        return bool(os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN") and os.getenv("TWILIO_FROM_WHATSAPP"))

    def send_message(self, to: str, message: str) -> str:
        if self._twilio_configured():
            try:
                from twilio.rest import Client  # type: ignore

                client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
                dest = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
                client.messages.create(from_=os.getenv("TWILIO_FROM_WHATSAPP"), to=dest, body=message)
                return f"WhatsApp message sent to {to}, sir."
            except Exception as exc:
                return f"Twilio WhatsApp failed: {exc}"
        encoded = urllib.parse.quote(message)
        phone = re.sub(r"[^\d+]", "", to)
        webbrowser.open(f"https://wa.me/{phone}?text={encoded}")
        return "Opening WhatsApp Web with your message prepared, sir."

    def process(self, command: str) -> dict[str, Any]:
        match = re.search(r"(?:send )?(?:whatsapp|message) (?:to )?(.+?)(?::| saying | message )(.+)", command, re.I)
        if match and "email" not in command.lower():
            return {"success": True, "response": self.send_message(match.group(1).strip(), match.group(2).strip())}
        return {"success": False, "response": "I did not find a WhatsApp command, sir."}

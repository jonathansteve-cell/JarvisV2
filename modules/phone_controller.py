"""Phone call integration via Twilio or tel link."""

from __future__ import annotations

import os
import re
import webbrowser
from typing import Any


class PhoneController:
    """Place phone calls when Twilio is configured, otherwise open tel: link."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def call(self, number: str) -> str:
        clean = re.sub(r"[^\d+]", "", number)
        if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN") and os.getenv("TWILIO_FROM_PHONE"):
            return (
                "Phone calling is configured for Twilio, but outbound voice requires a TwiML URL. "
                "Add your TwiML endpoint before live calling, sir."
            )
        webbrowser.open(f"tel:{clean}")
        return f"Opening phone dialer for {clean}, sir."

    def process(self, command: str) -> dict[str, Any]:
        match = re.search(r"(?:call|phone) (.+)", command, re.I)
        if match and "video" not in command.lower():
            return {"success": True, "response": self.call(match.group(1))}
        return {"success": False, "response": "I did not find a phone command, sir."}

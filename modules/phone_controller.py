"""Phone call integration via Twilio or tel link.

Live calling needs three things in ``.env``: ``TWILIO_ACCOUNT_SID``,
``TWILIO_AUTH_TOKEN``, ``TWILIO_FROM_PHONE`` — plus a TwiML URL that tells Twilio
what to do with the call (``TWILIO_TWIML_URL``). Without the TwiML URL Jarvis
falls back to opening the system dialer and says so.
"""

from __future__ import annotations

import logging
import os
import re
import webbrowser
from typing import Any

from utils.helpers import is_placeholder_secret

logger = logging.getLogger(__name__)


class PhoneController:
    """Place phone calls when Twilio is configured, otherwise open a tel: link."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def _credentials(self) -> tuple[str | None, str | None, str | None]:
        return (
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
            os.getenv("TWILIO_FROM_PHONE"),
        )

    def _twiml_url(self) -> str | None:
        return os.getenv("TWILIO_TWIML_URL") or self.config.get("integrations.phone.twiml_url")

    def configured(self) -> bool:
        return not any(is_placeholder_secret(value) for value in self._credentials())

    def call(self, number: str) -> str:
        clean = re.sub(r"[^\d+]", "", number)
        sid, token, from_phone = self._credentials()
        twiml = self._twiml_url()
        have_credentials = not any(is_placeholder_secret(v) for v in (sid, token, from_phone))
        has_twiml = not is_placeholder_secret(twiml)

        if have_credentials and has_twiml:
            try:
                from twilio.rest import Client  # type: ignore

                client = Client(sid, token)
                call = client.calls.create(to=clean, from_=from_phone, url=twiml)
                return f"Calling {clean}, sir. Call reference {call.sid}."
            except Exception as exc:
                logger.warning("Twilio call failed: %s", exc)
                return f"Twilio could not place the call: {exc}"

        if have_credentials:
            webbrowser.open(f"tel:{clean}")
            return (
                f"Twilio is configured but there is no TwiML URL, so I opened the dialer for "
                f"{clean}, sir. Add TWILIO_TWIML_URL to .env for hands-free calling."
            )

        webbrowser.open(f"tel:{clean}")
        return f"Opening phone dialer for {clean}, sir."

    def process(self, command: str) -> dict[str, Any]:
        match = re.search(r"(?:call|phone) (.+)", command, re.I)
        if match and "video" not in command.lower():
            return {"success": True, "response": self.call(match.group(1))}
        return {"success": False, "response": "I did not find a phone command, sir."}

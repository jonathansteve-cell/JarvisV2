"""Email integration via SMTP and IMAP."""

from __future__ import annotations

import email
import imaplib
import os
import re
import smtplib
from email.message import EmailMessage
from typing import Any


class EmailController:
    """Send and read email when credentials are configured in environment variables."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def _credentials(self) -> tuple[str | None, str | None]:
        return os.getenv("JARVIS_EMAIL_ADDRESS"), os.getenv("JARVIS_EMAIL_APP_PASSWORD")

    def configured(self) -> bool:
        address, password = self._credentials()
        return bool(address and password and not password.startswith("your_"))

    def send_email(self, to: str, subject: str, body: str) -> str:
        if not self.configured():
            return "Email is not configured. Add address and app password to your local .env file, sir."
        address, password = self._credentials()
        msg = EmailMessage()
        msg["From"] = address
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        host = self.config.get("integrations.email.smtp_host", "smtp.gmail.com")
        port = int(self.config.get("integrations.email.smtp_port", 587))
        with smtplib.SMTP(host, port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(address, password)
            smtp.send_message(msg)
        return f"Email sent to {to}, sir."

    def unread_count(self) -> str:
        if not self.configured():
            return "Email is not configured yet, sir."
        address, password = self._credentials()
        host = self.config.get("integrations.email.imap_host", "imap.gmail.com")
        with imaplib.IMAP4_SSL(host) as imap:
            imap.login(address, password)
            imap.select("INBOX")
            status, data = imap.search(None, "UNSEEN")
            if status != "OK":
                return "I could not read the inbox, sir."
            count = len(data[0].split()) if data and data[0] else 0
        return f"You have {count} unread email messages, sir."

    def read_latest(self, limit: int = 5) -> str:
        if not self.configured():
            return "Email is not configured yet, sir."
        address, password = self._credentials()
        host = self.config.get("integrations.email.imap_host", "imap.gmail.com")
        subjects = []
        with imaplib.IMAP4_SSL(host) as imap:
            imap.login(address, password)
            imap.select("INBOX")
            status, data = imap.search(None, "ALL")
            if status != "OK" or not data or not data[0]:
                return "Your inbox appears empty, sir."
            ids = data[0].split()[-limit:]
            for msg_id in reversed(ids):
                status, msg_data = imap.fetch(msg_id, "(RFC822)")
                if status == "OK":
                    raw = msg_data[0][1]
                    message = email.message_from_bytes(raw)
                    subjects.append(message.get("Subject", "No subject"))
        return "Latest email subjects: " + "; ".join(subjects)

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        send_match = re.search(
            r"send email to (\S+) subject (.+?) body (.+)", command, re.I | re.S
        )
        if send_match:
            return {
                "success": True,
                "response": self.send_email(
                    send_match.group(1), send_match.group(2).strip(), send_match.group(3).strip()
                ),
            }
        if "unread email" in lower or "how many emails" in lower:
            return {"success": True, "response": self.unread_count()}
        if "check email" in lower or "read email" in lower or "latest email" in lower:
            return {"success": True, "response": self.read_latest()}
        return {"success": False, "response": "I did not find an email command, sir."}

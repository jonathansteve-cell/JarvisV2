"""Email integration via SMTP and IMAP."""

from __future__ import annotations

import email
import imaplib
import os
import re
import smtplib
from email.message import EmailMessage
from typing import Any

from utils.helpers import is_placeholder_secret


class EmailController:
    """Send and read email when credentials are configured in environment variables."""

    def __init__(self, config: Any) -> None:
        self.config = config
        # A draft waiting for "send the email". Deliberately never written to disk.
        self._pending: dict[str, str] | None = None

    def _credentials(self) -> tuple[str | None, str | None]:
        return os.getenv("JARVIS_EMAIL_ADDRESS"), os.getenv("JARVIS_EMAIL_APP_PASSWORD")

    def configured(self) -> bool:
        address, password = self._credentials()
        return not is_placeholder_secret(address) and not is_placeholder_secret(password)

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

    # ----------------------------------------------------------------- drafts
    def draft_email(self, to: str, topic: str) -> str:
        """Prepare a short message and hold it until the user confirms."""
        topic = topic.strip().strip(".!?")
        body = (
            f"Hi,\n\n"
            f"I wanted to follow up regarding {topic}. "
            f"Let me know a good time to go over the details.\n\n"
            f"Best regards"
        )
        subject = topic[:60].strip().capitalize() or "Following up"
        self._pending = {"to": to, "subject": subject, "body": body}
        return (
            f"Draft ready for {to}, subject '{subject}'. Say 'send the email' to send it, "
            f"or 'cancel the email' to discard it, sir."
        )

    def send_pending(self) -> str:
        if not self._pending:
            return "There is no email draft waiting, sir."
        pending, self._pending = self._pending, None
        return self.send_email(pending["to"], pending["subject"], pending["body"])

    def cancel_pending(self) -> str:
        if not self._pending:
            return "There is no email draft to cancel, sir."
        self._pending = None
        return "Email draft discarded, sir."

    @staticmethod
    def _subject_from_body(body: str) -> str:
        first = re.split(r"[.!?\n]", body.strip())[0]
        words = first.split()[:6]
        return " ".join(words).capitalize() or "Message from Jarvis"

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()

        # Confirm or discard a held draft.
        if re.match(r"^(send|confirm)\s+(it|the email|that email|the draft)$", lower):
            return {"success": True, "response": self.send_pending()}
        if re.match(r"^(cancel|discard|delete)\s+(it|the email|that email|the draft)$", lower):
            return {"success": True, "response": self.cancel_pending()}

        # 1) Fully specified: "send email to X subject Y body Z"
        send_match = re.search(
            r"(?:send\s+)?(?:an?\s+)?email\s+(?:to\s+)?(\S+) subject (.+?) body (.+)",
            command,
            re.I | re.S,
        )
        if send_match:
            return {
                "success": True,
                "response": self.send_email(
                    send_match.group(1), send_match.group(2).strip(), send_match.group(3).strip()
                ),
            }

        # 2) Draft request: "write/draft/compose an email to X about Y"
        draft_match = re.search(
            r"(?:write|draft|compose|prepare)\s+(?:an?\s+)?email\s+(?:to\s+)?(\S+)\s+"
            r"(?:about|regarding|on|for)\s+(.+)",
            command,
            re.I | re.S,
        )
        if draft_match:
            return {
                "success": True,
                "response": self.draft_email(draft_match.group(1), draft_match.group(2).strip()),
            }

        # 3) Body given inline: "email X saying Y" / "email X: Y" / "message X that Y"
        saying_match = re.search(
            r"(?:send\s+)?(?:an?\s+)?(?:email|message|whatsapp)?\s*(?:to\s+)?(\S+@\S+)\s*"
            r"(?:saying|with the message|message|that|:)\s+(.+)",
            command,
            re.I | re.S,
        )
        if saying_match and "email" in lower:
            body = saying_match.group(2).strip()
            return {
                "success": True,
                "response": self.send_email(
                    saying_match.group(1), self._subject_from_body(body), body
                ),
            }

        if "unread email" in lower or "how many emails" in lower:
            return {"success": True, "response": self.unread_count()}
        if "check email" in lower or "read email" in lower or "latest email" in lower:
            return {"success": True, "response": self.read_latest()}
        if self._pending and "email" in lower:
            return {
                "success": True,
                "response": (
                    f"A draft to {self._pending['to']} is still waiting, sir. "
                    f"Say 'send the email' or 'cancel the email'."
                ),
            }
        return {"success": False, "response": "I did not find an email command, sir."}

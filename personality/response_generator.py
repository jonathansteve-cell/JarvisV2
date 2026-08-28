"""AI and personality responses for Jarvis V2."""

from __future__ import annotations

import logging
import os
import random
from dataclasses import dataclass
from typing import Any

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class AIResult:
    """AI response result."""

    text: str
    provider: str = "offline"
    success: bool = True


class ResponseGenerator:
    """Generate JARVIS-style responses using Groq when configured."""

    def __init__(self, config: Any, memory: Any | None = None) -> None:
        self.config = config
        self.memory = memory
        self.history: list[dict[str, str]] = []
        self.max_history = 12

    def greeting(self) -> str:
        from datetime import datetime

        hour = datetime.now().hour
        if 4 <= hour < 12:
            part = "Good morning"
        elif 12 <= hour < 17:
            part = "Good afternoon"
        else:
            part = "Good evening"
        name = self.assistant_name()
        openers = [
            f"{part}, sir. All primary systems are operational.",
            f"{part}, sir. Systems initialized and standing by.",
            f"{part}, sir. Everything is running smoothly.",
        ]
        return f"{random.choice(openers)} {name} at your service. How may I assist you?"

    def assistant_name(self) -> str:
        """Return the assistant's custom name if the user renamed it, else Jarvis."""
        try:
            if self.memory:
                for fact in self.memory.recall("assistant_name"):
                    if fact.get("key") == "assistant_name" and fact.get("value"):
                        return fact["value"].strip().title()
        except Exception:
            logger.debug("Assistant name lookup failed", exc_info=True)
        return "Jarvis"

    def acknowledge(self, action: str) -> str:
        templates = [
            f"Certainly, sir. {action}",
            f"Right away, sir. {action}",
            f"Understood. {action}",
        ]
        return random.choice(templates)

    def offline_response(self, prompt: str) -> str:
        lower = prompt.lower()
        if "what can you do" in lower or "capabilities" in lower:
            return (
                "I can control applications, windows, screenshots, files, web searches, reminders, "
                "email, WhatsApp, Spotify, calendar, phone calls, Zoom, Word documents, smart-home "
                "devices, Wake-on-LAN, memory, jokes, Roblox grind tracking, and AI conversation "
                "when configured."
            )
        if "turn on" in lower and "pc" in lower:
            return (
                "I cannot turn on a fully powered-off PC by software alone. I can wake a sleeping PC "
                "with Wake-on-LAN if the BIOS, network card, and MAC address are configured."
            )
        if "hello" in lower or "hi" in lower:
            return "Hello, sir. I am online and listening."
        if "date" in lower or "what day is it" in lower or "today's date" in lower:
            from datetime import datetime

            now = datetime.now()
            return f"Today is {now.strftime('%A, %d %B %Y')}, sir."
        if "time" in lower:
            from datetime import datetime

            return f"The time is {datetime.now().strftime('%I:%M %p')}, sir."
        return (
            "I understand, sir. The local command modules did not match that request. "
            "Configure GROQ_API_KEY in your local .env file for full conversational intelligence."
        )

    def generate(self, prompt: str, context: str = "") -> AIResult:
        """Generate a response from Groq, falling back to offline responses."""
        api_key = os.getenv("GROQ_API_KEY") or self.config.env("GROQ_API_KEY")
        if not api_key or api_key.lower().startswith(("your_", "placeholder")) or requests is None:
            return AIResult(self.offline_response(prompt), provider="offline")

        system_prompt = self.config.get("ai.system_prompt")
        model = os.getenv("GROQ_MODEL") or self.config.get("ai.model", "llama-3.3-70b-versatile")
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"Useful user memory/context:\n{context}"})
        messages.extend(self.history[-self.max_history :])
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": self.config.get("ai.temperature", 0.6),
                    "max_tokens": self.config.get("ai.max_tokens", 700),
                },
                timeout=25,
            )
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": text})
            self.history = self.history[-self.max_history :]
            return AIResult(text=text, provider="groq", success=True)
        except Exception as exc:  # pragma: no cover - network failure path
            logger.warning("Groq response failed: %s", exc)
            return AIResult(self.offline_response(prompt), provider="offline", success=False)

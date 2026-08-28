"""Configuration management for Jarvis V2."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from utils.env import load_env_file


DEFAULT_CONFIG: dict[str, Any] = {
    "app": {
        "name": "J.A.R.V.I.S V2",
        "mode": "gui",
        "debug": False,
        "owner_name": "sir",
    },
    "voice": {
        "wake_words": ["hey jarvis", "jarvis"],
        "language": "en-US",
        "continuous_listening": True,
        "phrase_time_limit": 7,
        "timeout": 5,
        "tts_enabled": True,
        "voice_profile": "dark_synthetic",
        "prefer_voice_gender": "male",
    },
    "ai": {
        "provider": "groq",
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "temperature": 0.6,
        "max_tokens": 700,
        "system_prompt": (
            "You are J.A.R.V.I.S V2, a concise, capable, privacy-respecting desktop AI "
            "assistant. Respond like a professional intelligent companion. Be truthful about "
            "what you can do. Do not claim actions were completed unless a tool/module did them."
        ),
    },
    "behavior": {
        "confirm_dangerous_actions": True,
        "speak_responses": True,
        "show_console_output": True,
        "remember_conversations": True,
        "learning_enabled": True,
        "allow_web_open": True,
    },
    "paths": {
        "data_dir": "data",
        "log_dir": "logs",
        "screenshot_dir": "screenshots",
        "documents_dir": "documents",
        "music_dir": "~/Music",
    },
    "roblox": {
        "allow_web_open": True,
        "default_session_minutes": 30,
    },
    "applications": {
        "paths": {},
    },
    "ui": {
        "theme": "hero_orb",
        "accent": "#FF8C1A",
        "background": "#050505",
        "panel": "#0C0C0C",
        "text": "#F5EDE0",
        "muted": "#9A8F7F",
        "start_minimized": False,
        "transparency": 0.98,
    },
    "integrations": {
        "email": {
            "smtp_host": os.getenv("JARVIS_SMTP_HOST", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("JARVIS_SMTP_PORT", "587")),
            "imap_host": os.getenv("JARVIS_IMAP_HOST", "imap.gmail.com"),
        },
        "wake_on_lan": {
            "mac_address": os.getenv("JARVIS_TARGET_PC_MAC", ""),
            "broadcast": os.getenv("JARVIS_TARGET_PC_BROADCAST", "255.255.255.255"),
            "port": 9,
        },
        "smart_home": {
            "provider": "home_assistant_or_simulated",
        },
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class ConfigManager:
    """Load, save, and query Jarvis configuration."""

    def __init__(self, config_path: str | Path = "config/config.json") -> None:
        load_env_file()
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = deepcopy(DEFAULT_CONFIG)
        self.load()

    @property
    def config(self) -> dict[str, Any]:
        return self._config

    def load(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                loaded = json.loads(self.config_path.read_text(encoding="utf-8"))
                self._config = _deep_merge(DEFAULT_CONFIG, loaded)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON config at {self.config_path}: {exc}") from exc
        else:
            self.save()
        return self._config

    def save(self) -> None:
        self.config_path.write_text(json.dumps(self._config, indent=2), encoding="utf-8")

    def get(self, dotted_key: str, default: Any = None) -> Any:
        current: Any = self._config
        for part in dotted_key.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def set(self, dotted_key: str, value: Any, save: bool = True) -> None:
        current = self._config
        parts = dotted_key.split(".")
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
        if save:
            self.save()

    def env(self, key: str, default: str | None = None) -> str | None:
        return os.getenv(key, default)

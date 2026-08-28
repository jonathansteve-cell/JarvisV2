"""Text-to-speech wrapper for Jarvis V2."""

from __future__ import annotations

import logging
import platform
import subprocess
import threading
from typing import Any

from voice.voice_profiles import DEFAULT_PROFILE, get_profile

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Speak responses using pyttsx3 when available, with OS fallbacks.

    The active persona comes from ``voice.voice_profile`` in config (see
    voice/voice_profiles.py). Explicit ``voice.tts_rate`` / ``voice.tts_volume``
    values in config still override the profile when present.
    """

    def __init__(self, config: Any) -> None:
        self.config = config
        self.enabled = bool(config.get("voice.tts_enabled", True))
        self.profile_name = str(config.get("voice.voice_profile", DEFAULT_PROFILE))
        self.profile = get_profile(self.profile_name)
        self._lock = threading.Lock()
        self._engine = None
        if self.enabled:
            self._initialize_engine()

    def _initialize_engine(self) -> None:
        try:
            import pyttsx3  # type: ignore

            self._engine = pyttsx3.init()
            self._apply_profile()
        except Exception as exc:  # pragma: no cover - depends on host audio
            logger.warning("pyttsx3 unavailable: %s", exc)
            self._engine = None

    def _apply_profile(self) -> None:
        """Push the resolved voice profile into the pyttsx3 engine."""
        if not self._engine:
            return
        try:
            rate = self.config.get("voice.tts_rate") or self.profile.get("rate", 178)
            volume = self.config.get("voice.tts_volume")
            if volume is None:
                volume = self.profile.get("volume", 0.9)
            self._engine.setProperty("rate", int(rate))
            self._engine.setProperty("volume", float(volume))
            pitch = self.profile.get("pitch")
            if pitch is not None:
                # Pitch support depends on the driver (e.g. SAPI5); ignore elsewhere.
                self._engine.setProperty("pitch", int(pitch))
        except Exception:
            logger.debug("Applying voice profile failed", exc_info=True)
        self._select_voice()

    def apply_profile(self, name: str) -> str:
        """Switch persona at runtime and persist it to config."""
        self.profile_name = name
        self.profile = get_profile(name)
        self.config.set("voice.voice_profile", name, save=True)
        self._apply_profile()
        return f"Voice profile set to {self.profile_name}."

    def _select_voice(self) -> None:
        if not self._engine:
            return
        try:
            voices = self._engine.getProperty("voices") or []
            lowered = [f"{voice.name} {voice.id}".lower() for voice in voices]

            # 1) Profile hints first (e.g. a deep male system voice).
            for hint in self.profile.get("hints", []):
                for index, text in enumerate(lowered):
                    if hint in text:
                        self._engine.setProperty("voice", voices[index].id)
                        return

            # 2) Fall back to the configured gender preference.
            preferred = str(self.profile.get("gender") or self.config.get("voice.prefer_voice_gender", "male")).lower()
            for index, text in enumerate(lowered):
                if preferred in text or (preferred == "male" and "david" in text):
                    self._engine.setProperty("voice", voices[index].id)
                    return
        except Exception:
            logger.debug("Voice selection failed", exc_info=True)

    def speak(self, text: str, blocking: bool = True) -> None:
        """Speak text. If TTS is disabled/unavailable, do nothing."""
        if not self.enabled or not text:
            return
        if blocking:
            self._speak_now(text)
        else:
            threading.Thread(target=self._speak_now, args=(text,), daemon=True).start()

    def _speak_now(self, text: str) -> None:
        with self._lock:
            if self._engine:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                    return
                except Exception as exc:  # pragma: no cover
                    logger.warning("pyttsx3 speak failed: %s", exc)
            self._os_fallback(text)

    def _os_fallback(self, text: str) -> None:
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["say", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == "Linux":
                subprocess.run(["espeak", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            logger.debug("OS speech fallback failed", exc_info=True)

    def stop(self) -> None:
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

"""Text-to-speech wrapper for Jarvis V2."""

from __future__ import annotations

import logging
import platform
import subprocess
import threading
from typing import Any

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Speak responses using pyttsx3 when available, with OS fallbacks."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.enabled = bool(config.get("voice.tts_enabled", True))
        self._lock = threading.Lock()
        self._engine = None
        if self.enabled:
            self._initialize_engine()

    def _initialize_engine(self) -> None:
        try:
            import pyttsx3  # type: ignore

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", int(self.config.get("voice.tts_rate", 178)))
            self._engine.setProperty("volume", float(self.config.get("voice.tts_volume", 0.9)))
            self._select_voice()
        except Exception as exc:  # pragma: no cover - depends on host audio
            logger.warning("pyttsx3 unavailable: %s", exc)
            self._engine = None

    def _select_voice(self) -> None:
        if not self._engine:
            return
        try:
            preferred = str(self.config.get("voice.prefer_voice_gender", "male")).lower()
            voices = self._engine.getProperty("voices") or []
            for voice in voices:
                text = f"{voice.name} {voice.id}".lower()
                if preferred in text or (preferred == "male" and "david" in text):
                    self._engine.setProperty("voice", voice.id)
                    break
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

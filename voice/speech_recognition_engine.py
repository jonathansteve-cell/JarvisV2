"""Speech recognition wrapper for Jarvis V2."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SpeechRecognitionEngine:
    """Listen to microphone input with SpeechRecognition when available."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.available = False
        self.recognizer = None
        self.microphone = None
        self._initialize()

    def _initialize(self) -> None:
        try:
            import speech_recognition as sr  # type: ignore

            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            self.microphone = sr.Microphone()
            self.available = True
        except Exception as exc:  # pragma: no cover - host audio dependent
            logger.warning("Speech recognition unavailable: %s", exc)
            self.available = False

    def listen_once(self) -> str | None:
        """Listen for one phrase and return recognized text."""
        if not self.available or not self.recognizer or not self.microphone:
            return None
        timeout = self.config.get("voice.timeout", 5)
        phrase_time_limit = self.config.get("voice.phrase_time_limit", 7)
        language = self.config.get("voice.language", "en-US")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            return self.recognizer.recognize_google(audio, language=language)
        except Exception as exc:  # pragma: no cover - host audio dependent
            logger.debug("Speech recognition did not produce text: %s", exc)
            return None

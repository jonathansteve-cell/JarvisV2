"""Text-to-speech wrapper for Jarvis V2.

Three output engines are supported, selected by ``voice.tts_engine`` in config:

* ``edge``    - Microsoft Edge neural voices via the ``edge-tts`` package. Free,
  no API key, far more natural than SAPI/eSpeak. Needs network + an mp3 player.
* ``pyttsx3`` - fully offline OS voices (SAPI5 on Windows, eSpeak on Linux).
* ``system``  - the raw OS command (``say`` / ``espeak``).
* ``auto``    - the default: prefer edge-tts when it is installed, else pyttsx3,
  else the OS command.

Every engine degrades to the next one on failure, so a missing mp3 player or a
network outage never silences Jarvis.
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any

from voice.voice_profiles import DEFAULT_PROFILE, get_profile

logger = logging.getLogger(__name__)

#: Neural voice used when the profile does not name one.
DEFAULT_EDGE_VOICE = "en-US-GuyNeural"

#: Per-profile neural voice fallbacks, matched on the profile's hints.
EDGE_VOICE_HINTS = {
    "female": "en-US-AriaNeural",
    "british": "en-GB-RyanNeural",
    "indian": "en-IN-PrabhatNeural",
}


def find_audio_player() -> tuple[str, list[str]] | None:
    """Locate a command that can play an mp3 file.

    Returns ``(name, argv_prefix)`` where the audio path is appended last, or
    ``None`` when nothing suitable is installed.
    """
    candidates = [
        ("mpv", ["mpv", "--no-video", "--really-quiet"]),
        ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]),
        ("mplayer", ["mplayer", "-really-quiet"]),
        ("afplay", ["afplay"]),  # macOS
        ("cvlc", ["cvlc", "--play-and-exit", "--quiet"]),
    ]
    for name, argv in candidates:
        if shutil.which(name):
            return name, argv
    return None


def _windows_media_player_command(path: str) -> list[str]:
    """Play an mp3 with the WPF MediaPlayer that ships with Windows."""
    script = (
        "Add-Type -AssemblyName presentationCore;"
        "$p = New-Object System.Windows.Media.MediaPlayer;"
        "$p.open([uri]'" + path.replace("'", "''") + "');"
        "$p.Play();"
        "Start-Sleep -Milliseconds 400;"
        "while ($p.NaturalDuration.HasTimeSpan -and $p.Position -lt $p.NaturalDuration.TimeSpan) {"
        "Start-Sleep -Milliseconds 100};"
        "$p.Close()"
    )
    return ["powershell", "-NoProfile", "-NonInteractive", "-Command", script]


class TextToSpeech:
    """Speak responses with the best available engine.

    The active persona comes from ``voice.voice_profile`` in config (see
    voice/voice_profiles.py). Explicit ``voice.tts_rate`` / ``voice.tts_volume``
    values in config still override the profile when present.
    """

    def __init__(self, config: Any) -> None:
        self.config = config
        self.enabled = bool(config.get("voice.tts_enabled", True))
        self.profile_name = str(config.get("voice.voice_profile", DEFAULT_PROFILE))
        self.profile = get_profile(self.profile_name)
        self.engine_preference = str(config.get("voice.tts_engine", "auto")).lower()
        self.edge_voice = str(config.get("voice.edge_voice", "") or self._edge_voice_for_profile())
        self._lock = threading.Lock()
        self._engine = None
        self._edge_available: bool | None = None
        self._last_backend = "none"
        self._last_error = "not initialised"
        if self.enabled:
            self._initialize_engine()

    # ------------------------------------------------------------ engines
    def _edge_voice_for_profile(self) -> str:
        hints = " ".join(self.profile.get("hints", [])).lower()
        gender = str(self.profile.get("gender", "")).lower()
        if "female" in hints or gender == "female":
            return EDGE_VOICE_HINTS["female"]
        if "british" in hints or "uk" in hints:
            return EDGE_VOICE_HINTS["british"]
        if "indian" in hints:
            return EDGE_VOICE_HINTS["indian"]
        return DEFAULT_EDGE_VOICE

    def _edge_importable(self) -> bool:
        if self._edge_available is None:
            try:
                import edge_tts  # type: ignore  # noqa: F401

                self._edge_available = True
            except Exception:
                self._edge_available = False
        return self._edge_available

    def _initialize_engine(self) -> None:
        if self.engine_preference in {"auto", "pyttsx3"}:
            try:
                import pyttsx3  # type: ignore

                self._engine = pyttsx3.init()
                self._apply_profile()
                self._last_error = "ready"
                return
            except Exception as exc:  # pragma: no cover - depends on host audio
                logger.warning("pyttsx3 unavailable: %s", exc)
                self._engine = None
                self._last_error = f"pyttsx3 unavailable: {exc}"
        if self.engine_preference == "edge" and not self._edge_importable():
            self._last_error = "edge-tts is not installed (pip install edge-tts)"

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
        self.edge_voice = str(self.config.get("voice.edge_voice", "") or self._edge_voice_for_profile())
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

    # ------------------------------------------------------------- status
    def describe_engine(self) -> dict[str, Any]:
        """Report which engine is live - used by ``python main.py --check``."""
        if not self.enabled:
            return {"backend": "none", "detail": "voice.tts_enabled is false"}
        if self._engine:
            driver = "pyttsx3"
            try:
                driver = f"pyttsx3/{type(self._engine).__name__}"
            except Exception:
                pass
            return {"backend": "pyttsx3", "detail": driver, "voice": self._current_pyttsx3_voice()}
        if self._edge_importable():
            return {"backend": "edge", "detail": "edge-tts", "voice": self.edge_voice}
        return {"backend": "none", "detail": self._last_error}

    def _current_pyttsx3_voice(self) -> str | None:
        if not self._engine:
            return None
        try:
            voices = self._engine.getProperty("voices") or []
            selected = self._engine.getProperty("voice")
            for voice in voices:
                if getattr(voice, "id", None) == selected:
                    return str(voice.name)
            return str(voices[0].name) if voices else None
        except Exception:
            return None

    # ------------------------------------------------------------- speak
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
            if self.engine_preference in {"auto", "edge"} and self._edge_importable():
                if self._speak_edge(text):
                    return
            if self._engine:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                    self._last_backend = "pyttsx3"
                    return
                except Exception as exc:  # pragma: no cover
                    logger.warning("pyttsx3 speak failed: %s", exc)
                    self._last_error = f"pyttsx3 speak failed: {exc}"
            self._os_fallback(text)

    def _speak_edge(self, text: str) -> bool:
        """Synthesize with edge-tts and play the result. Returns True on success."""
        try:
            import asyncio

            import edge_tts  # type: ignore
        except Exception as exc:
            self._last_error = f"edge-tts import failed: {exc}"
            return False

        rate = self._edge_rate()
        path = Path(tempfile.gettempdir()) / f"jarvis_tts_{os.getpid()}.mp3"
        try:
            communicate = edge_tts.Communicate(text, self.edge_voice, rate=rate)
            asyncio.run(communicate.save(str(path)))
            if not path.exists() or path.stat().st_size == 0:
                raise RuntimeError("edge-tts produced no audio")
        except Exception as exc:
            logger.warning("edge-tts synthesis failed, falling back: %s", exc)
            self._last_error = f"edge-tts synthesis failed: {exc}"
            return False

        try:
            played = self._play_file(path)
            self._last_backend = "edge"
            return played
        except Exception as exc:  # pragma: no cover - host audio dependent
            logger.warning("edge-tts playback failed, falling back: %s", exc)
            self._last_error = f"edge-tts playback failed: {exc}"
            return False
        finally:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass

    def _edge_rate(self) -> str:
        """Translate a pyttsx3 words-per-minute rate into an edge-tts delta."""
        try:
            rate = int(self.config.get("voice.tts_rate") or self.profile.get("rate", 178))
        except Exception:
            rate = 178
        delta = round((rate - 178) / 178 * 100)
        delta = max(-50, min(80, delta))
        return f"{delta:+d}%"

    def _play_file(self, path: Path) -> bool:
        player = find_audio_player()
        if player:
            result = subprocess.run(
                [*player[1], str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if result.returncode == 0:
                return True
            logger.debug("%s exited with %s", player[0], result.returncode)
        if platform.system() == "Windows":
            result = subprocess.run(
                _windows_media_player_command(str(path.resolve())),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return result.returncode == 0
        return False

    def _os_fallback(self, text: str) -> None:
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["say", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == "Linux":
                subprocess.run(["espeak", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._last_backend = "system"
        except Exception:
            logger.debug("OS speech fallback failed", exc_info=True)

    def stop(self) -> None:
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

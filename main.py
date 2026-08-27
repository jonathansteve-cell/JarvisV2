"""J.A.R.V.I.S V2 launcher.

Run:
  python main.py             # desktop UI
  python main.py --voice-only # pure voice assistant
  python main.py --command "system status" # one command
"""

from __future__ import annotations

import argparse
import logging
import time

from core.jarvis import Jarvis
from utils.logger import setup_logging
from voice.speech_recognition_engine import SpeechRecognitionEngine

logger = logging.getLogger(__name__)


def run_command(command: str) -> int:
    setup_logging(console=True)
    jarvis = Jarvis()
    result = jarvis.process_command(command, speak=False)
    print(result.text)
    return 0 if result.success else 1


def run_voice_only() -> int:
    # Voice-only mode writes logs to files but does not print command responses to console.
    setup_logging(console=False)
    jarvis = Jarvis(voice_output=True)
    recognizer = SpeechRecognitionEngine(jarvis.config)
    jarvis.tts.speak(jarvis.boot_message(), blocking=False)

    if not recognizer.available:
        jarvis.tts.speak(
            "Speech recognition is not available. Please install the voice dependencies and check the microphone, sir.",
            blocking=True,
        )
        return 1

    running = True
    while running:
        text = recognizer.listen_once()
        if not text:
            time.sleep(0.2)
            continue
        if text.lower().strip() in {"exit", "quit", "goodbye", "shutdown jarvis", "stop jarvis"}:
            jarvis.tts.speak("Shutting down. It has been an honor, sir.", blocking=True)
            running = False
            continue
        jarvis.process_command(text, speak=True)
    jarvis.shutdown()
    return 0


def run_gui() -> int:
    setup_logging(console=True)
    from gui.main_window import JarvisMainWindow

    app = JarvisMainWindow()
    app.run()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S V2 desktop AI assistant")
    parser.add_argument("--voice-only", action="store_true", help="Run without GUI or command text output")
    parser.add_argument("--command", help="Run a single text command and exit")
    args = parser.parse_args()

    if args.command:
        return run_command(args.command)
    if args.voice_only:
        return run_voice_only()
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())

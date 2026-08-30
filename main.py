"""J.A.R.V.I.S V2 launcher.

Run:
  python main.py             # web dashboard (browser, always-on mic)
  python main.py --gui       # desktop Tkinter HUD (optional)
  python main.py --web       # web dashboard explicitly
  python main.py --voice-only # pure voice assistant
  python main.py --command "system status" # one command
  python main.py --check      # self-diagnostic report, non-zero exit on failure
  python main.py --check --verbose # include the passing checks too
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
    if not result.success:
        return 1
    # A module can handle a command and still fail to perform it (e.g. the app
    # was never installed). Surface that to the shell.
    data = result.data if isinstance(result.data, dict) else {}
    if data.get("launched") is False:
        return 1
    return 0


def run_check(verbose: bool) -> int:
    from utils.health_check import run_health_check

    return run_health_check(verbose=verbose)


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
    """Optional desktop Tkinter HUD."""
    setup_logging(console=True)
    from gui.main_window import JarvisMainWindow

    app = JarvisMainWindow()
    app.run()
    return 0


def run_web(port: int) -> int:
    setup_logging(console=True)
    from dashboard.server import serve

    serve(port)
    return 0


def run_voice_ui() -> int:
    """Run the voice-only 3D interface."""
    setup_logging(console=True)
    from gui.voice_only_ui import VoiceOnlyUI
    
    app = VoiceOnlyUI()
    app.run()
    return 0


def run_modern_ui() -> int:
    """Run the modern chat interface."""
    setup_logging(console=True)
    from gui.modern_ui import ModernJarvisUI
    
    app = ModernJarvisUI()
    app.run()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S V2 - Voice AI Assistant")
    parser.add_argument("--command", help="Run a single text command and exit")
    parser.add_argument("--check", action="store_true", help="Run the self-diagnostic report and exit")
    parser.add_argument("--verbose", action="store_true", help="With --check, also print the checks that passed")
    args = parser.parse_args()

    if args.check:
        return run_check(args.verbose)
    if args.command:
        return run_command(args.command)
    
    # Default: Launch Voice-Only 3D UI
    return run_voice_ui()


if __name__ == "__main__":
    raise SystemExit(main())

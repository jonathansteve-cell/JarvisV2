"""J.A.R.V.I.S V2 launcher.

Run:
  python main.py             # CyberHUD web dashboard (browser)
  python main.py --web       # same, explicitly
  python main.py --web --port 9000
  python main.py --gui       # desktop Tkinter HUD
  python main.py --voice-only # pure voice assistant
  python main.py --voice-ui  # voice-only 3D interface
  python main.py --modern-ui # modern chat interface
  python main.py --command "system status" # one command
  python main.py --check      # self-diagnostic report, non-zero exit on failure
  python main.py --check --verbose # include the passing checks too

The web dashboard serves the React UI built from ui/. Build it once first:

  cd ui && npm install && npm run build
"""

from __future__ import annotations

import argparse
import logging
import time

from core.jarvis import Jarvis
from dashboard.server import DEFAULT_PORT as DEFAULT_WEB_PORT
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

    interface = parser.add_mutually_exclusive_group()
    interface.add_argument("--web", action="store_true", help="CyberHUD browser dashboard (default)")
    interface.add_argument("--gui", action="store_true", help="Desktop Tkinter Hero Core HUD")
    interface.add_argument("--voice-only", action="store_true", help="Voice-only assistant, no screen UI")
    interface.add_argument("--voice-ui", action="store_true", help="Voice-only 3D interface")
    interface.add_argument("--modern-ui", action="store_true", help="Modern chat interface")
    parser.add_argument("--port", type=int, default=DEFAULT_WEB_PORT, help=f"Port for --web (default {DEFAULT_WEB_PORT})")

    args = parser.parse_args()

    if args.check:
        return run_check(args.verbose)
    if args.command:
        return run_command(args.command)
    if args.gui:
        return run_gui()
    if args.voice_only:
        return run_voice_only()
    if args.voice_ui:
        return run_voice_ui()
    if args.modern_ui:
        return run_modern_ui()

    # Default: the CyberHUD browser dashboard.
    return run_web(args.port)


if __name__ == "__main__":
    raise SystemExit(main())

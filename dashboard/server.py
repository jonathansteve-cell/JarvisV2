"""Local web dashboard server for Jarvis V2.

A Spark-style browser dashboard served entirely from the local machine using
only the Python standard library. Commands posted from the dashboard run
through the same Jarvis pipeline as the desktop HUD and CLI.

    python main.py --web          # http://localhost:8765

Server-side TTS is intentionally off: the browser speaks responses itself via
the Web Speech API, so audio plays on the machine running the browser.
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from core.jarvis import Jarvis
from modules.productivity_controller import ProductivityController
from modules.system_controller import SystemController

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_PORT = 8765


class DashboardState:
    """Shared Jarvis instance + lock for web requests."""

    def __init__(self, jarvis: Jarvis) -> None:
        self.jarvis = jarvis
        self.lock = threading.Lock()
        self.productivity = ProductivityController(jarvis.config)

    def run_command(self, command: str) -> dict[str, Any]:
        with self.lock:
            result = self.jarvis.process_command(command, speak=False)
        return {
            "text": result.text,
            "success": result.success,
            "intent": result.intent,
            "provider": result.provider,
        }

    def snapshot(self) -> dict[str, Any]:
        import os
        from datetime import datetime

        jarvis = self.jarvis
        status = SystemController(jarvis.config).status()
        cpu = status.get("cpu_percent")
        mem = status.get("memory_percent")
        disk = status.get("disk_percent")
        battery = status.get("battery_percent")

        key = os.getenv("GROQ_API_KEY", "")
        groq_ready = bool(key) and not key.lower().startswith(("your_", "placeholder"))

        roblox = jarvis.roblox
        session = None
        if roblox.session:
            started = datetime.fromisoformat(roblox.session["started_at"])
            remaining = max(0, int(roblox.session["minutes"]) - round((datetime.now() - started).total_seconds() / 60))
            session = {
                "focus": roblox.session.get("focus", ""),
                "minutes": roblox.session.get("minutes"),
                "remaining": remaining,
            }
        goals = roblox.data.get("goals", [])
        tasks = [task for task in self.productivity.data.get("tasks", []) if not task.get("done")][-6:]
        notes = self.productivity.data.get("notes", [])[-4:]

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "assistant_name": jarvis.ai.assistant_name(),
            "system": {"cpu": cpu, "mem": mem, "disk": disk, "battery": battery},
            "ai": {"groq_ready": groq_ready, "model": jarvis.config.get("ai.model")},
            "voice": {"available": jarvis.tts.enabled},
            "memory": {
                "stats": jarvis.memory.stats(),
                "facts": [
                    {"key": fact["key"], "value": fact["value"]}
                    for fact in jarvis.memory.recall()[:6]
                ],
            },
            "productivity": {
                "tasks": [{"text": task["text"], "done": task.get("done", False)} for task in tasks],
                "notes": [{"text": note["text"]} for note in notes],
            },
            "roblox": {
                "session": session,
                "goals": [{"text": goal["text"], "done": goal["done"]} for goal in goals[:6]],
                "sessions_logged": len(roblox.data.get("sessions", [])),
                "total_minutes": sum(int(s.get("minutes", 0)) for s in roblox.data.get("sessions", [])),
            },
        }


def make_handler(state: DashboardState) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        server_version = "JarvisV2Dashboard/2.0"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            logger.debug("web %s", format % args)

        # ------------------------------------------------------------- helpers
        def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        # ---------------------------------------------------------------- GET
        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self._send_html((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
            elif path == "/api/state":
                self._send_json(state.snapshot())
            elif path == "/api/health":
                self._send_json({"status": "online", "name": "J.A.R.V.I.S V2"})
            else:
                self._send_json({"error": "not found"}, status=404)

        # --------------------------------------------------------------- POST
        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path != "/api/command":
                self._send_json({"error": "not found"}, status=404)
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(length) or b"{}")
                command = str(payload.get("command", "")).strip()
                if not command:
                    self._send_json({"error": "empty command"}, status=400)
                    return
                self._send_json(state.run_command(command))
            except Exception as exc:
                logger.exception("Command failed")
                self._send_json({"error": str(exc)}, status=500)

    return DashboardHandler


def serve(port: int = DEFAULT_PORT) -> None:
    """Start the dashboard web server (blocking)."""
    jarvis = Jarvis(voice_output=False)
    state = DashboardState(jarvis)
    server = ThreadingHTTPServer(("0.0.0.0", port), make_handler(state))
    logger.info("Solar Dashboard serving on http://localhost:%s", port)
    print(f"⚡ Solar Dashboard online → http://localhost:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        jarvis.shutdown()


if __name__ == "__main__":
    serve()

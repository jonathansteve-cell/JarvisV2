"""Local web dashboard server for Jarvis V2.

Serves the CyberHUD React interface (built from ``ui/``) plus a JSON API backed
by the same Jarvis pipeline as the desktop HUD and CLI. Standard library only —
no Flask, no extra server dependency.

    python main.py --web          # http://localhost:8765

Build the UI once before the first run:

    cd ui && npm install && npm run build

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
from dashboard.telemetry import (
    drive_telemetry,
    gpu_telemetry,
    network_telemetry,
    process_telemetry,
    weather_snapshot,
)
from modules.system_controller import SystemController

logger = logging.getLogger(__name__)

# The CyberHUD React app, built from `ui/` (see ui/README.md).
UI_DIST = Path(__file__).resolve().parent.parent / "ui" / "dist"
DEFAULT_PORT = 8765
SERVER_START = __import__("time").time()

_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".map": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}

MISSING_BUILD_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>J.A.R.V.I.S V2 — build the UI</title>
<style>
  body{background:#03070d;color:#f59e0b;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
       display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .box{max-width:34rem;border:1px solid rgba(245,158,11,.35);border-radius:12px;
       padding:2rem 2.25rem;background:rgba(28,20,5,.65);box-shadow:0 0 40px rgba(245,158,11,.12)}
  h1{font-size:.95rem;letter-spacing:.18em;margin:0 0 1rem;text-transform:uppercase}
  p{font-size:.8rem;line-height:1.7;color:rgba(245,158,11,.75)}
  code{display:block;background:#000;border:1px solid rgba(245,158,11,.25);border-radius:6px;
       padding:.75rem 1rem;margin:.75rem 0;color:#fbbf24;font-size:.78rem;white-space:pre}
  em{color:rgba(245,158,11,.5);font-style:normal}
</style></head>
<body><div class="box">
  <h1>CyberHUD not built yet</h1>
  <p>The React interface has not been compiled. Build it once:</p>
  <code>cd ui
npm install
npm run build</code>
  <p>Then reload this page. For live-reload development instead, run
  <code>npm run dev</code> inside <em>ui/</em> — it proxies <em>/api</em> to this server.</p>
</div></body></html>
"""


class DashboardState:
    """Shared Jarvis instance + lock for web requests."""

    def __init__(self, jarvis: Jarvis) -> None:
        self.jarvis = jarvis
        self.lock = threading.Lock()
        # Reuse the controller the command pipeline already mutates. Constructing
        # a second one here gave /api/state a stale in-memory copy, so tasks
        # added through /api/command never showed up in the dashboard.
        self.productivity = jarvis.productivity
        # Weather is fetched on its own thread so a slow or blocked public API
        # never stalls a /api/state response. snapshot() always returns instantly
        # with whatever was last resolved (None until the first lookup lands).
        self._weather: dict[str, Any] | None = None
        self._stop = threading.Event()
        self._weather_thread = threading.Thread(
            target=self._weather_loop, name="weather-refresh", daemon=True
        )
        self._weather_thread.start()

    def weather(self) -> dict[str, Any] | None:
        return self._weather

    def _weather_loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._weather = weather_snapshot(self.jarvis.config, force=True)
            except Exception:  # pragma: no cover - defensive
                logger.debug("weather refresh failed", exc_info=True)
            # telemetry.weather_snapshot already caches for 15 min; poll slower.
            self._stop.wait(900.0)

    def close(self) -> None:
        self._stop.set()

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

        # Drive storage matrix: real files from local runtime folders.
        from utils.helpers import human_bytes

        try:
            import psutil as _psutil

            _du = _psutil.disk_usage("/")
            usage = f"{_du.used / (1 << 30):.1f} GB/{_du.total / (1 << 30):.1f} GB"
        except Exception:
            usage = None

        drive_files: list[dict[str, Any]] = []
        seen: set[str] = set()
        for path_key in ("paths.data_dir", "paths.log_dir", "paths.screenshot_dir"):
            folder = Path(str(jarvis.config.get(path_key, "")))
            if folder.exists():
                for file_path in sorted(folder.rglob("*"), key=lambda p: p.stat().st_mtime if p.is_file() else 0, reverse=True):
                    if file_path.is_file() and str(file_path) not in seen:
                        seen.add(str(file_path))
                        drive_files.append(
                            {
                                "name": str(file_path),
                                "size": human_bytes(file_path.stat().st_size),
                                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%d/%m/%y %H:%M"),
                            }
                        )
                    if len(drive_files) >= 6:
                        break
            if len(drive_files) >= 6:
                break

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "assistant_name": jarvis.ai.assistant_name(),
            "system": {"cpu": cpu, "mem": mem, "disk": disk, "battery": battery},
            "ai": {"groq_ready": groq_ready, "model": jarvis.config.get("ai.model")},
            "voice": {
                "available": jarvis.tts.enabled,
                # Lets the browser mic gate on the same wake words as the
                # desktop assistant instead of firing on ambient speech.
                "wake_words": list(jarvis.config.get("voice.wake_words", []) or []),
            },
            "memory": {
                "stats": jarvis.memory.stats(),
                "facts": [
                    {"key": fact["key"], "value": fact["value"]}
                    for fact in jarvis.memory.recall()[:6]
                ],
            },
            "productivity": {
                "tasks": [
                    {
                        "id": f"task-{index}",
                        "text": task["text"],
                        "done": task.get("done", False),
                        "time": datetime.fromisoformat(task["created_at"]).strftime("%I:%M %p") if task.get("created_at") else "",
                    }
                    for index, task in enumerate(tasks)
                ],
                "notes": [{"text": note["text"]} for note in notes],
            },
            "roblox": {
                "session": session,
                "goals": [{"text": goal["text"], "done": goal["done"]} for goal in goals[:6]],
                "sessions_logged": len(roblox.data.get("sessions", [])),
                "total_minutes": sum(int(s.get("minutes", 0)) for s in roblox.data.get("sessions", [])),
            },
            "conversations": [
                {
                    "command": item["command"][:52],
                    "response": item["response"][:80],
                    "time": item["created_at"][11:16] if len(item["created_at"]) > 15 else item["created_at"],
                }
                for item in jarvis.memory.recent_conversations(7)
            ],
            "drive": {"disk_percent": disk, "usage": usage, "files": drive_files},
            # CyberHUD panels. Each is independent: a probe that fails comes back
            # null and that panel renders "NO SIGNAL" instead of breaking.
            "drives": drive_telemetry(),
            "processes": process_telemetry(),
            "net": network_telemetry(),
            "gpu": gpu_telemetry(),
            "weather": self.weather(),
            "uptime": str(datetime.now() - datetime.fromtimestamp(SERVER_START)).split(".")[0],
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

        def _send_html(self, html: str, status: int = 200) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        # ---------------------------------------------------------------- GET
        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/api/state":
                self._send_json(state.snapshot())
            elif path == "/api/health":
                self._send_json(
                    {
                        "status": "online",
                        "name": "J.A.R.V.I.S V2",
                        "assistant_name": state.jarvis.ai.assistant_name(),
                        "ui_built": (UI_DIST / "index.html").exists(),
                    }
                )
            elif path.startswith("/api/"):
                self._send_json({"error": "not found"}, status=404)
            elif path in ("/", "/index.html"):
                self._serve_ui_root()
            else:
                self._serve_ui_asset(path)

        def _serve_ui_root(self) -> None:
            index = UI_DIST / "index.html"
            if not index.exists():
                self._send_html(MISSING_BUILD_PAGE, status=503)
                return
            self._send_html(index.read_text(encoding="utf-8"))

        def _serve_ui_asset(self, path: str) -> None:
            """Serve a built asset, with an SPA fallback for client routes."""
            relative = path.lstrip("/")
            candidate = (UI_DIST / relative).resolve()
            # Never let a crafted path escape the build directory.
            if not str(candidate).startswith(str(UI_DIST.resolve())):
                self._send_json({"error": "forbidden"}, status=403)
                return
            if candidate.is_file():
                body = candidate.read_bytes()
                content_type = _CONTENT_TYPES.get(candidate.suffix.lower(), "application/octet-stream")
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(body)
                return
            # Single-page app: unknown non-API paths fall back to index.html.
            index = UI_DIST / "index.html"
            if index.exists():
                self._send_html(index.read_text(encoding="utf-8"))
            else:
                self._send_html(MISSING_BUILD_PAGE, status=503)

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
    logger.info("CyberHUD serving on http://localhost:%s", port)
    print(f"⚡ CyberHUD online → http://localhost:{port}  (Ctrl+C to stop)")
    if not (UI_DIST / "index.html").exists():
        print("  ⚠ ui/dist not found — run: cd ui && npm install && npm run build")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        state.close()
        server.server_close()
        jarvis.shutdown()


if __name__ == "__main__":
    serve()

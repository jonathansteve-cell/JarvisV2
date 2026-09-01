"""End-to-end HTTP tests against the real dashboard handler.

These exist because the /api/* routes are easy to drop when the static-file
routing changes. Every route the React UI depends on is asserted here, through
a real socket, not a mocked handler.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from core.jarvis import Jarvis
from dashboard.server import UI_DIST, DashboardState, make_handler


class Server:
    def __init__(self, tmp_path):
        # data_dir must be in the config file *before* Jarvis() runs: the
        # controllers resolve their storage paths during construction.
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"paths": {"data_dir": str(tmp_path)}}), encoding="utf-8"
        )
        self.jarvis = Jarvis(str(config_file), voice_output=False)
        self.state = DashboardState(self.jarvis)
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.state))
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def close(self) -> None:
        self.state.close()
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=3)
        self.jarvis.shutdown()


@pytest.fixture()
def server(tmp_path):
    instance = Server(tmp_path)
    yield instance
    instance.close()


def get(url: str) -> tuple[int, str, str]:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return (
                response.status,
                response.headers.get("Content-Type", ""),
                response.read().decode("utf-8", "replace"),
            )
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type", ""), error.read().decode("utf-8", "replace")


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode()
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode() or "{}")


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
def test_api_state_returns_the_full_cyberhud_contract(server):
    status, content_type, body = get(f"{server.base}/api/state")
    assert status == 200, body
    assert content_type.startswith("application/json")

    data = json.loads(body)
    for key in (
        "time", "assistant_name", "system", "ai", "voice", "memory",
        "productivity", "roblox", "conversations", "drive",
        "drives", "processes", "net", "gpu", "weather", "uptime",
    ):
        assert key in data, f"/api/state is missing '{key}'"


def test_api_health_reports_ui_build_state(server):
    status, _, body = get(f"{server.base}/api/health")
    assert status == 200
    data = json.loads(body)
    assert data["status"] == "online"
    assert data["ui_built"] == (UI_DIST / "index.html").exists()


def test_state_exposes_wake_words_for_the_browser_mic(server):
    """The HUD gates dictation on these, so they must come from the backend."""
    _, _, body = get(f"{server.base}/api/state")
    voice = json.loads(body)["voice"]
    assert "available" in voice
    assert isinstance(voice["wake_words"], list)
    assert voice["wake_words"], "expected the configured wake words, not an empty list"
    assert all(isinstance(word, str) and word for word in voice["wake_words"])
    assert voice["wake_words"] == list(server.jarvis.config.get("voice.wake_words"))


def test_unknown_api_route_is_json_404_not_the_spa(server):
    """An /api/* miss must not fall through to index.html — that breaks fetch()."""
    status, content_type, body = get(f"{server.base}/api/does-not-exist")
    assert status == 404
    assert content_type.startswith("application/json")
    assert json.loads(body) == {"error": "not found"}


def test_post_command_runs_the_jarvis_pipeline(server):
    status, data = post_json(f"{server.base}/api/command", {"command": "system status"})
    assert status == 200
    assert "text" in data and "success" in data
    assert data["text"], "expected a spoken-style response"


def test_post_command_rejects_empty_input(server):
    status, data = post_json(f"{server.base}/api/command", {"command": "   "})
    assert status == 400
    assert data == {"error": "empty command"}


def test_post_unknown_route_is_404(server):
    status, data = post_json(f"{server.base}/api/nope", {"command": "hi"})
    assert status == 404
    assert data == {"error": "not found"}


def test_task_round_trip_over_http(server):
    """The HUD's add/toggle buttons drive these two commands."""
    status, data = post_json(f"{server.base}/api/command", {"command": "add task wire the HUD"})
    assert status == 200 and data["success"]

    tasks = json.loads(get(f"{server.base}/api/state")[2])["productivity"]["tasks"]
    assert any(task["text"] == "wire the HUD" for task in tasks)
    assert all(task["id"] for task in tasks)

    status, data = post_json(f"{server.base}/api/command", {"command": "complete task wire the HUD"})
    assert data["success"]
    tasks = json.loads(get(f"{server.base}/api/state")[2])["productivity"]["tasks"]
    assert not any(task["text"] == "wire the HUD" for task in tasks), "completed tasks leave the open list"


# ---------------------------------------------------------------------------
# Static UI serving
# ---------------------------------------------------------------------------
def test_root_serves_the_built_ui_or_the_build_hint(server):
    status, content_type, body = get(f"{server.base}/")
    assert content_type.startswith("text/html")
    if (UI_DIST / "index.html").exists():
        assert status == 200
        assert "<div id=\"root\">" in body
        assert "main.tsx" in body or "/assets/" in body
    else:
        assert status == 503
        assert "CyberHUD not built yet" in body


def test_spa_fallback_returns_html_for_client_routes(server):
    status, content_type, _ = get(f"{server.base}/some/client/route")
    assert content_type.startswith("text/html")
    assert status in (200, 503)


def test_path_traversal_is_blocked(server):
    for attack in ("/../main.py", "/../../etc/passwd", "/%2e%2e/main.py"):
        status, content_type, body = get(f"{server.base}{attack}")
        assert "root:" not in body, f"{attack} leaked a system file"
        assert "J.A.R.V.I.S V2 launcher" not in body, f"{attack} leaked source"
        assert status in (200, 403, 404, 503)
        assert not content_type.startswith("text/x-python")


def test_built_assets_are_served_with_the_right_type(server):
    if not (UI_DIST / "index.html").exists():
        pytest.skip("ui/dist not built")
    assets = sorted((UI_DIST / "assets").glob("*.js"))
    assert assets, "expected a built JS bundle"
    status, content_type, body = get(f"{server.base}/assets/{assets[0].name}")
    assert status == 200
    assert content_type.startswith("text/javascript")
    assert len(body) > 1000

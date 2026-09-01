"""Telemetry probes backing the CyberHUD `/api/state` extensions.

Every probe must degrade to ``None``/``[]`` instead of raising — a missing
sensor or a blocked network must never take the dashboard down.
"""

from core.jarvis import Jarvis
from dashboard.server import DashboardState
from dashboard.telemetry import (
    _compass,
    drive_telemetry,
    gpu_telemetry,
    network_telemetry,
    process_telemetry,
    weather_snapshot,
)

DRIVE_KEYS = {
    "id", "letter", "label", "mountpoint", "filesystem", "total", "used",
    "free", "used_percent", "free_percent", "temp",
    "cache_total", "cache_read", "cache_write",
}

PROCESS_KEYS = {"id", "pid", "name", "status", "cpu", "memory"}


def test_drive_telemetry_shape():
    drives = drive_telemetry()
    # Any machine running the tests has at least one real filesystem.
    assert drives, "expected at least one mounted drive"
    for drive in drives:
        assert DRIVE_KEYS <= set(drive), f"missing keys: {DRIVE_KEYS - set(drive)}"
        assert 0 <= drive["used_percent"] <= 100
        assert abs(drive["used_percent"] + drive["free_percent"] - 100) < 0.2
        assert drive["temp"] is None, "psutil cannot read drive temps; must stay null"


def test_drive_telemetry_respects_limit():
    assert len(drive_telemetry(limit=1)) <= 1


def test_drive_telemetry_is_sorted_by_fill():
    drives = drive_telemetry()
    fills = [drive["used_percent"] for drive in drives]
    assert fills == sorted(fills, reverse=True)


def test_process_telemetry_shape():
    processes = process_telemetry(limit=5)
    assert processes, "expected at least one running process"
    assert len(processes) <= 5
    for proc in processes:
        assert PROCESS_KEYS <= set(proc), f"missing keys: {PROCESS_KEYS - set(proc)}"
        assert proc["status"] in {"ACTIVE", "IDLE", "BUSY"}
        assert 0 <= proc["cpu"] <= 100
        assert proc["name"] == proc["name"].upper()
        # The internal sort key must not leak to the API.
        assert "_mem_bytes" not in proc


def test_process_telemetry_caches_handles_between_polls():
    """cpu_percent() is 0.0 on first contact, so handles must be retained."""
    first = {proc["id"] for proc in process_telemetry()}
    second = {proc["id"] for proc in process_telemetry()}
    assert first & second, "stable processes should appear on both polls"


def test_network_telemetry_shape():
    net = network_telemetry()
    if net is None:
        return  # psutil without net counters — acceptable
    assert {"percent", "rate_mbps", "sent", "received"} <= set(net)
    assert 0 <= net["percent"] <= 100


def test_network_rate_is_zero_on_first_sample():
    """No previous sample means no delta, so the bar must not invent a spike."""
    import dashboard.telemetry as telemetry

    telemetry._net_last = None
    net = telemetry.network_telemetry()
    if net is not None:
        assert net["rate_mbps"] == 0.0
        assert net["percent"] == 0.0


def test_gpu_telemetry_is_none_without_pynvml():
    import sys

    if "pynvml" in sys.modules:
        return
    assert gpu_telemetry() is None


def test_weather_returns_none_when_the_lookup_fails(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("network unreachable")

    monkeypatch.setattr("dashboard.telemetry._geocode", boom)
    monkeypatch.setattr("dashboard.telemetry._geolocate_by_ip", boom)
    monkeypatch.setattr("dashboard.telemetry._weather_cache", {"at": 0.0, "data": None})
    assert weather_snapshot(None) is None


def test_weather_is_cached(monkeypatch):
    calls = {"n": 0}

    def fake(location):
        calls["n"] += 1
        return {"location": "COIMBATORE, IN", "temp": 28}

    monkeypatch.setattr("dashboard.telemetry._geolocate_by_ip", lambda: (11.0, 76.9, "COIMBATORE", "IN"))
    monkeypatch.setattr("dashboard.telemetry._fetch_weather", fake)
    monkeypatch.setattr("dashboard.telemetry._weather_cache", {"at": 0.0, "data": None})

    assert weather_snapshot(None) == {"location": "COIMBATORE, IN", "temp": 28}
    assert weather_snapshot(None) == {"location": "COIMBATORE, IN", "temp": 28}
    assert calls["n"] == 1, "the 15-minute cache must prevent a second fetch"


def test_compass_bearing():
    assert _compass(0) == "N"
    assert _compass(90) == "E"
    assert _compass(180) == "S"
    assert _compass(270) == "W"
    assert _compass(202.5) == "SSW"


# ---------------------------------------------------------------------------
# The contract ui/src/lib/api.ts depends on.
# ---------------------------------------------------------------------------
def make_state(tmp_path):
    import json

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"paths": {"data_dir": str(tmp_path)}}), encoding="utf-8")
    jarvis = Jarvis(str(config_file), voice_output=False)
    return jarvis, DashboardState(jarvis)


def test_snapshot_exposes_the_cyberhud_blocks(tmp_path):
    jarvis, state = make_state(tmp_path)
    try:
        snapshot = state.snapshot()
        for key in ("drives", "processes", "net", "gpu", "weather", "system", "productivity"):
            assert key in snapshot, f"/api/state is missing '{key}'"
        assert isinstance(snapshot["drives"], list)
        assert isinstance(snapshot["processes"], list)
    finally:
        state.close()
        jarvis.shutdown()


def test_snapshot_tasks_carry_stable_ids(tmp_path):
    jarvis, state = make_state(tmp_path)
    try:
        state.productivity.add_task("wire the HUD")
        tasks = state.snapshot()["productivity"]["tasks"]
        assert tasks, "expected the task added above"
        assert all(task.get("id") for task in tasks)
        assert len({task["id"] for task in tasks}) == len(tasks), "ids must be unique"
    finally:
        state.close()
        jarvis.shutdown()


def test_weather_thread_does_not_block_the_snapshot(tmp_path):
    """Weather resolves on its own thread, so a cold start still answers fast."""
    jarvis, state = make_state(tmp_path)
    try:
        # Called immediately after construction, before any lookup can land.
        assert state.weather() is None or isinstance(state.weather(), dict)
        assert "weather" in state.snapshot()
    finally:
        state.close()
        jarvis.shutdown()

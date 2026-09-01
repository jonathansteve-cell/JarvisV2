"""Live system telemetry for the CyberHUD web UI.

Every probe here is best-effort. A single failing probe degrades its own panel
to ``None`` rather than taking the whole snapshot down with it — the UI renders
a "NO SIGNAL" state instead of breaking.

Backs the ``drives`` / ``processes`` / ``net`` / ``weather`` blocks that
``dashboard/server.py`` adds to ``/api/state``.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime
from typing import Any

from utils.helpers import human_bytes

logger = logging.getLogger(__name__)

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil missing on a bare install
    psutil = None  # type: ignore

# --------------------------------------------------------------------------- #
# Filesystems we are willing to show as "drives".
# --------------------------------------------------------------------------- #
_REAL_FILESYSTEMS = {
    "ntfs", "fat32", "exfat", "ext2", "ext3", "ext4", "btrfs", "xfs", "zfs",
    "apfs", "hfs", "hfsplus", "reiserfs", "f2fs", "jfs", "reiser4", "vboxsf",
}

# WMO weather interpretation codes -> short HUD label.
# https://open-meteo.com/en/docs  (current_weather.weathercode)
_WEATHER_CODES = {
    0: "CLEAR", 1: "MAINLY CLEAR", 2: "PARTLY CLOUDY", 3: "OVERCAST",
    45: "FOG", 48: "FREEZING FOG",
    51: "LIGHT DRIZZLE", 53: "DRIZZLE", 55: "HEAVY DRIZZLE",
    56: "FREEZING DRIZZLE", 57: "FREEZING DRIZZLE",
    61: "LIGHT RAIN", 63: "RAIN", 65: "HEAVY RAIN",
    66: "FREEZING RAIN", 67: "FREEZING RAIN",
    71: "LIGHT SNOW", 73: "SNOW", 75: "HEAVY SNOW", 77: "SNOW GRAINS",
    80: "RAIN SHOWERS", 81: "RAIN SHOWERS", 82: "VIOLENT SHOWERS",
    85: "SNOW SHOWERS", 86: "SNOW SHOWERS",
    95: "THUNDERSTORM", 96: "STORM + HAIL", 99: "STORM + HAIL",
}

_COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


# --------------------------------------------------------------------------- #
# Drives
# --------------------------------------------------------------------------- #
def _drive_letter(device: str, mountpoint: str) -> str:
    """Windows gives ``C:\\\\``; POSIX gives ``/`` or ``/mnt/data``."""
    if len(device) >= 2 and device[1] == ":":
        return device[0].upper()
    trimmed = mountpoint.rstrip("/") or "/"
    if trimmed == "/":
        return "SYS"
    return trimmed.rsplit("/", 1)[-1][:3].upper()


def _label_for(letter: str, mountpoint: str) -> str:
    trimmed = mountpoint.rstrip("/") or "/"
    if trimmed == "/":
        return "SYSTEM PRIMARY"
    return trimmed.rsplit("/", 1)[-1].replace("-", " ").replace("_", " ").upper()


def _io_for(device: str) -> dict[str, Any]:
    """Disk read/write totals for a partition, if psutil can map it."""
    if not psutil or not hasattr(psutil, "disk_io_counters"):
        return {"total": None, "read": None, "write": None}
    try:
        counters = psutil.disk_io_counters(perdisk=True) or {}
    except Exception:
        return {"total": None, "read": None, "write": None}

    # Windows keys are 'C:\\', Linux keys are 'vda' / 'sda1' / 'nvme0n1p2'.
    key = None
    for candidate in (device, device.rstrip("/")):
        if candidate in counters:
            key = candidate
            break
    if key is None:
        base = os.path.basename(device).rstrip("0123456789")
        for name in counters:
            if name.startswith(base) and base:
                key = name
                break
    if key is None:
        return {"total": None, "read": None, "write": None}

    stats = counters[key]
    total = int(getattr(stats, "read_bytes", 0)) + int(getattr(stats, "write_bytes", 0))
    return {
        "total": human_bytes(total),
        "read": human_bytes(int(getattr(stats, "read_bytes", 0))),
        "write": human_bytes(int(getattr(stats, "write_bytes", 0))),
    }


def drive_telemetry(limit: int = 6) -> list[dict[str, Any]]:
    """One entry per mounted real filesystem, biggest first."""
    if not psutil:
        return []

    drives: list[dict[str, Any]] = []
    seen: set[str] = set()
    try:
        partitions = psutil.disk_partitions(all=False)
    except Exception:
        logger.debug("disk_partitions failed", exc_info=True)
        return []

    for part in partitions:
        fstype = (part.fstype or "").lower()
        if fstype not in _REAL_FILESYSTEMS:
            continue
        if part.mountpoint in seen:
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except Exception:
            continue
        if usage.total <= 0:
            continue
        seen.add(part.mountpoint)

        letter = _drive_letter(part.device, part.mountpoint)
        used_pct = round(usage.percent, 1)
        io = _io_for(part.device)
        drives.append(
            {
                "id": f"drive-{letter.lower()}",
                "letter": letter,
                "label": _label_for(letter, part.mountpoint),
                "mountpoint": part.mountpoint,
                "filesystem": fstype,
                "total": human_bytes(usage.total),
                "used": human_bytes(usage.used),
                "free": human_bytes(usage.free),
                "used_percent": used_pct,
                "free_percent": round(100 - used_pct, 1),
                # Drive temperature needs S.M.A.R.T. (smartctl / WMI), which
                # psutil does not expose. Null -> the UI shows "--".
                "temp": None,
                "cache_total": io["total"],
                "cache_read": io["read"],
                "cache_write": io["write"],
            }
        )

    drives.sort(key=lambda d: d["used_percent"], reverse=True)
    return drives[:limit]


# --------------------------------------------------------------------------- #
# Processes
# --------------------------------------------------------------------------- #
# psutil.cpu_percent() is 0.0 the first time it is called for a process, so the
# handles are kept alive between polls to get real deltas.
_proc_cache: dict[int, Any] = {}
_proc_lock = threading.Lock()

_STATUS_MAP = {
    "running": "ACTIVE",
    "sleeping": "IDLE",
    "idle": "IDLE",
    "disk-sleep": "BUSY",
    "stopped": "BUSY",
    "zombie": "BUSY",
    "dead": "BUSY",
}


def process_telemetry(limit: int = 8) -> list[dict[str, Any]]:
    """Top processes by memory, with a CPU delta since the previous poll."""
    if not psutil:
        return []

    rows: list[dict[str, Any]] = []
    with _proc_lock:
        alive: set[int] = set()
        for proc in psutil.process_iter(["pid", "name", "memory_info", "status"]):
            pid = proc.info.get("pid")
            if pid is None:
                continue
            alive.add(pid)
            try:
                cpu = proc.cpu_percent(interval=None)
            except Exception:
                cpu = 0.0
            _proc_cache[pid] = proc

            name = (proc.info.get("name") or "system").upper()[:22]
            mem = proc.info.get("memory_info")
            mem_bytes = int(getattr(mem, "rss", 0) or 0)
            raw_status = str(proc.info.get("status") or "running")
            rows.append(
                {
                    "id": f"proc-{pid}",
                    "pid": pid,
                    "name": name,
                    "status": _STATUS_MAP.get(raw_status, "BUSY"),
                    "cpu": round(min(cpu, 100.0), 1),
                    "memory": human_bytes(mem_bytes) if mem_bytes else "0 B",
                    "_mem_bytes": mem_bytes,
                }
            )

        for dead in set(_proc_cache) - alive:
            _proc_cache.pop(dead, None)

    rows.sort(key=lambda r: r["_mem_bytes"], reverse=True)
    for row in rows:
        row.pop("_mem_bytes", None)
    return rows[:limit]


# --------------------------------------------------------------------------- #
# Network
# --------------------------------------------------------------------------- #
_net_last: tuple[float, int] | None = None


def network_telemetry() -> dict[str, Any] | None:
    """Throughput since the previous poll, expressed as a 0-100 bar value."""
    global _net_last
    if not psutil or not hasattr(psutil, "net_io_counters"):
        return None
    try:
        counters = psutil.net_io_counters()
    except Exception:
        return None

    total = int(counters.bytes_sent) + int(counters.bytes_recv)
    now = time.time()
    rate_mbps = 0.0
    if _net_last is not None:
        prev_time, prev_total = _net_last
        elapsed = max(now - prev_time, 0.001)
        rate_mbps = max(0.0, (total - prev_total)) / elapsed / 1_000_000
    _net_last = (now, total)

    return {
        "percent": round(min(rate_mbps * 8, 100.0), 1),  # saturate at ~12.5 MB/s
        "rate_mbps": round(rate_mbps, 2),
        "sent": human_bytes(int(counters.bytes_sent)),
        "received": human_bytes(int(counters.bytes_recv)),
    }


# --------------------------------------------------------------------------- #
# GPU
# --------------------------------------------------------------------------- #
def gpu_telemetry() -> dict[str, Any] | None:
    """NVIDIA only, and only when pynvml is installed. Otherwise ``None``.

    psutil has no GPU support at all, so the gauge is honest about it instead of
    inventing a number.
    """
    try:
        import pynvml  # type: ignore
    except Exception:
        return None
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        name = pynvml.nvmlDeviceGetName(handle)
        return {
            "name": name.decode() if isinstance(name, bytes) else str(name),
            "percent": float(util.gpu),
            "memory_percent": round(mem.used / mem.total * 100, 1) if mem.total else 0.0,
            "temp": int(temp),
        }
    except Exception:
        logger.debug("NVML probe failed", exc_info=True)
        return None


# --------------------------------------------------------------------------- #
# Weather
# --------------------------------------------------------------------------- #
# Cached because the dashboard polls /api/state every couple of seconds and a
# public weather API must not be hammered at that rate.
_weather_lock = threading.Lock()
_weather_cache: dict[str, Any] = {"at": 0.0, "data": None}
_WEATHER_TTL = 900.0  # 15 minutes


def _compass(degrees: float) -> str:
    return _COMPASS[int(((degrees % 360) + 11.25) // 22.5) % 16]


def _geocode(city: str) -> tuple[float, float, str, str] | None:
    import requests

    url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(url, params={"name": city, "count": 1}, timeout=8)
    resp.raise_for_status()
    results = resp.json().get("results") or []
    if not results:
        return None
    hit = results[0]
    return (
        float(hit["latitude"]),
        float(hit["longitude"]),
        str(hit.get("name", city)).upper(),
        str(hit.get("country_code", "")).upper(),
    )


def _geolocate_by_ip() -> tuple[float, float, str, str] | None:
    import requests

    resp = requests.get("http://ip-api.com/json/", params={"fields": "lat,lon,city,countryCode"}, timeout=8)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("lat"):
        return None
    return (
        float(data["lat"]),
        float(data["lon"]),
        str(data.get("city", "")).upper(),
        str(data.get("countryCode", "")).upper(),
    )


def _fetch_weather(location: tuple[float, float, str, str]) -> dict[str, Any] | None:
    import requests

    lat, lon, city, country = location
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join(
            [
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "precipitation", "weather_code", "wind_speed_10m",
                "wind_direction_10m", "surface_pressure", "visibility",
            ]
        ),
        "daily": "sunrise,sunset",
        "timezone": "auto",
        "forecast_days": 1,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    current = data.get("current") or {}
    daily = data.get("daily") or {}

    code = int(current.get("weather_code", -1))
    sunrise = (daily.get("sunrise") or [""])[0]
    sunset = (daily.get("sunset") or [""])[0]

    return {
        "location": f"{city}, {country}".strip(", "),
        "country": country,
        "updated_time": datetime.now().strftime("%H:%M:%S"),
        "temp": round(float(current.get("temperature_2m", 0))),
        "temp_unit": "C",
        "condition": _WEATHER_CODES.get(code, "UNKNOWN"),
        "humidity": int(current.get("relative_humidity_2m", 0) or 0),
        "feels_like": round(float(current.get("apparent_temperature", 0) or 0)),
        "precipitation": round(float(current.get("precipitation", 0) or 0), 1),
        # Open-Meteo reports visibility in metres; the HUD shows kilometres.
        "visibility": round(float(current.get("visibility", 0) or 0) / 1000, 1),
        "wind_speed": round(float(current.get("wind_speed_10m", 0) or 0), 1),
        "wind_direction": _compass(float(current.get("wind_direction_10m", 0) or 0)),
        "pressure": round(float(current.get("surface_pressure", 0) or 0), 1),
        "sunrise": sunrise[11:16] if len(sunrise) >= 16 else "--:--",
        "sunset": sunset[11:16] if len(sunset) >= 16 else "--:--",
    }


def weather_snapshot(config: Any = None, force: bool = False) -> dict[str, Any] | None:
    """Current weather for the configured city, or the caller's IP if unset.

    Set ``weather.city`` in ``config/config.json`` (e.g. ``"Coimbatore"``) to pin
    the location and skip the IP lookup. Any failure returns ``None``.
    """
    with _weather_lock:
        if not force and _weather_cache["data"] is not None:
            if time.time() - _weather_cache["at"] < _WEATHER_TTL:
                return _weather_cache["data"]

        city = ""
        if config is not None:
            try:
                city = str(config.get("weather.city", "") or "").strip()
            except Exception:
                city = ""
        city = city or os.getenv("JARVIS_WEATHER_CITY", "").strip()

        try:
            location = _geocode(city) if city else _geolocate_by_ip()
            if location is None and city:
                location = _geolocate_by_ip()
            if location is None:
                return None
            data = _fetch_weather(location)
        except Exception:
            logger.debug("weather lookup failed", exc_info=True)
            return None

        if data is not None:
            _weather_cache["at"] = time.time()
            _weather_cache["data"] = data
        return data

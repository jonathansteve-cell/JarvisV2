"""Self-diagnostic report for Jarvis V2 (``python main.py --check``).

Every check returns one of three levels:

* ``ok``   - works, no action needed.
* ``warn`` - degraded; Jarvis still runs, but one feature is limited.
* ``fail`` - broken; fix this before expecting the related feature to work.

The runner prints a coloured, single-line-per-check report and exits non-zero
when any check fails, so it can be used in scripts and CI.

Secrets are never printed. API keys are reported as *set* / *placeholder* /
*missing* plus a length and the last four characters, which is enough to
confirm a rotation without exposing the key.
"""

from __future__ import annotations

import importlib
import os
import platform
import sys
from pathlib import Path
from typing import Any, Callable

from utils.helpers import PLACEHOLDER_PREFIXES  # noqa: F401  (re-exported for callers)

OK = "ok"
WARN = "warn"
FAIL = "fail"

LEVEL_SYMBOL = {OK: "[ OK ]", WARN: "[WARN]", FAIL: "[FAIL]"}

_ANSI = {
    OK: "\033[32m",
    WARN: "\033[33m",
    FAIL: "\033[31m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


#: Modules Jarvis imports at runtime; a missing one is a hard failure.
CORE_MODULES = [
    "core.config_manager",
    "core.jarvis",
    "personality.response_generator",
    "voice.text_to_speech",
    "voice.speech_recognition_engine",
    "modules.application_manager",
    "modules.system_controller",
    "modules.file_manager",
    "modules.web_controller",
]

#: Runtime folders Jarvis writes to.
RUNTIME_DIRS = ("data", "logs", "screenshots", "documents")

#: Optional integrations - missing credentials only warn.
OPTIONAL_ENV = [
    ("JARVIS_EMAIL_ADDRESS", "Email"),
    ("SPOTIFY_CLIENT_ID", "Spotify"),
    ("TWILIO_ACCOUNT_SID", "WhatsApp / phone"),
    ("HOME_ASSISTANT_TOKEN", "Home Assistant"),
]


def _flag(name: str) -> bool | None:
    """Read a boolean env flag. Returns None when unset."""
    value = os.environ.get(name)
    if value is None:
        return None
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def _colors_enabled() -> bool:
    if _flag("NO_COLOR"):
        return False
    forced = _flag("JARVIS_FORCE_COLOR")
    if forced is not None:
        return forced
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if platform.system() != "Windows":
        return True
    # Windows 10 1511+ needs VT processing switched on explicitly.
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        return True
    except Exception:
        return False


_COLOR = _colors_enabled()


def _paint(text: str, level: str | None = None, bold: bool = False) -> str:
    if not _COLOR:
        return text
    code = _ANSI.get("bold", "") if bold else ""
    if level:
        code += _ANSI.get(level, "")
    return f"{code}{text}{_ANSI['reset']}"


def key_status(value: str | None) -> tuple[str, str]:
    """Classify an API key without printing it.

    Returns ``(level, description)``.
    """
    if not value or not value.strip():
        return FAIL, "missing"
    cleaned = value.strip()
    if cleaned.lower().startswith(PLACEHOLDER_PREFIXES):
        return FAIL, "still the template placeholder"
    if len(cleaned) < 20:
        return WARN, f"set but suspiciously short ({len(cleaned)} chars, ends …{cleaned[-4:]})"
    return OK, f"set ({len(cleaned)} chars, ends …{cleaned[-4:]})"


class CheckResult:
    """One line of the report."""

    def __init__(self, name: str, level: str, message: str) -> None:
        self.name = name
        self.level = level
        self.message = message

    def render(self, width: int = 26) -> str:
        return f"{_paint(LEVEL_SYMBOL[self.level], self.level)} {self.name.ljust(width)} {self.message}"


def check_python() -> CheckResult:
    info = platform.python_version()
    if sys.version_info < (3, 10):
        return CheckResult("Python", FAIL, f"{info} - Jarvis needs 3.10 or newer")
    return CheckResult("Python", OK, f"{info} on {platform.system()} {platform.release()}")


def check_config() -> tuple[CheckResult, Any]:
    from core.config_manager import ConfigManager

    try:
        config = ConfigManager()
    except Exception as exc:
        return CheckResult("Config", FAIL, f"could not load config/config.json: {exc}"), None
    return CheckResult("Config", OK, f"loaded ({len(config.config)} sections)"), config


def check_env_file() -> CheckResult:
    path = Path(".env")
    if not path.exists():
        return CheckResult(
            ".env file",
            WARN,
            "not found in this folder - copy .env.example to .env (Jarvis falls back to .env.example-free defaults)",
        )
    return CheckResult(".env file", OK, f"found at {path.resolve()}")


def check_groq_key(config: Any) -> tuple[CheckResult, str | None]:
    raw = os.getenv("GROQ_API_KEY")
    if raw is None and config is not None:
        raw = config.env("GROQ_API_KEY")
    level, description = key_status(raw)
    # Only hand a *usable* key to the live API probe; probing with the template
    # placeholder produces a confusing 401 instead of the real diagnosis.
    usable = raw.strip() if (raw and raw.strip() and level != FAIL) else None
    return CheckResult("GROQ_API_KEY", level, description), usable


def check_groq_api(key: str | None) -> CheckResult:
    if not key:
        return CheckResult("Groq API", WARN, "skipped - no usable GROQ_API_KEY")
    try:
        import requests  # type: ignore
    except Exception:
        return CheckResult("Groq API", WARN, "skipped - 'requests' is not installed")
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=12,
        )
    except Exception as exc:
        # No answer at all is usually the network, not the key - report it as a
        # warning so a flaky connection does not look like a revoked key.
        return CheckResult(
            "Groq API",
            WARN,
            f"could not reach api.groq.com ({type(exc).__name__}) - offline, proxy, or firewall",
        )
    if response.status_code in (401, 403):
        return CheckResult("Groq API", FAIL, f"{response.status_code} - this key was revoked, expired, or mistyped")
    if response.status_code == 429:
        return CheckResult("Groq API", WARN, "429 rate limited - the key is valid but throttled right now")
    if not response.ok:
        return CheckResult("Groq API", FAIL, f"HTTP {response.status_code}")
    try:
        models = [m.get("id") for m in response.json().get("data", [])]
    except Exception:
        models = []
    configured = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    detail = f"{len(models)} models available"
    if models and configured not in models:
        return CheckResult("Groq API", WARN, f"{detail}, but GROQ_MODEL={configured} is not one of them")
    return CheckResult("Groq API", OK, f"reachable, {detail}, GROQ_MODEL={configured} valid")


def check_dependencies() -> list[CheckResult]:
    required = {"requests": "AI + web features", "psutil": "system status"}
    results = []
    for name, purpose in required.items():
        try:
            importlib.import_module(name)
            results.append(CheckResult(name, OK, f"installed ({purpose})"))
        except Exception as exc:
            results.append(CheckResult(name, FAIL, f"missing - {purpose} unavailable ({type(exc).__name__})"))

    optional = {
        "speech_recognition": "voice input",
        "pyttsx3": "offline speech output",
        "edge_tts": "natural neural speech output",
        "pyautogui": "volume keys / automation",
        "PIL": "screenshots",
        "spotipy": "Spotify",
        "twilio": "WhatsApp / phone",
        "docx": "Word documents",
    }
    for name, purpose in optional.items():
        try:
            importlib.import_module(name)
            results.append(CheckResult(name, OK, f"installed ({purpose})"))
        except Exception:
            results.append(CheckResult(name, WARN, f"not installed - {purpose} unavailable"))
    return results


def check_tts(config: Any) -> CheckResult:
    from voice.text_to_speech import TextToSpeech

    try:
        tts = TextToSpeech(config)
    except Exception as exc:
        return CheckResult("Speech output", FAIL, f"could not build the TTS engine: {exc}")
    engine = tts.describe_engine()
    if engine["backend"] == "none":
        return CheckResult("Speech output", FAIL, f"no working engine: {engine['detail']}")
    detail = f"backend={engine['backend']} voice={engine.get('voice') or engine['detail']}"
    level = OK if engine["backend"] in {"edge", "pyttsx3"} else WARN
    return CheckResult("Speech output", level, detail)


def check_audio_playback() -> CheckResult:
    from voice.text_to_speech import find_audio_player

    player = find_audio_player()
    if player:
        return CheckResult("Audio player", OK, f"{player[0]} found for neural speech playback")
    if platform.system() == "Windows":
        return CheckResult("Audio player", WARN, "will use PowerShell Media Player (built in)")
    return CheckResult(
        "Audio player",
        WARN,
        "no mp3 player found - install mpv or ffmpeg (ffplay) for edge-tts audio",
    )


def check_microphone() -> CheckResult:
    try:
        import speech_recognition as sr  # type: ignore
    except Exception:
        return CheckResult("Microphone", WARN, "SpeechRecognition not installed - voice input unavailable")
    try:
        names = sr.Microphone.list_microphone_names()
    except Exception as exc:
        return CheckResult("Microphone", FAIL, f"could not enumerate devices: {type(exc).__name__}")
    if not names:
        return CheckResult("Microphone", FAIL, "no input devices detected")
    return CheckResult("Microphone", OK, f"{len(names)} input device(s): {', '.join(names[:3])}")


def check_core_imports() -> CheckResult:
    broken = []
    for name in CORE_MODULES:
        try:
            importlib.import_module(name)
        except Exception as exc:
            broken.append(f"{name} ({type(exc).__name__}: {exc})")
    if broken:
        return CheckResult("Core modules", FAIL, "; ".join(broken))
    return CheckResult("Core modules", OK, f"{len(CORE_MODULES)} modules import cleanly")


def check_runtime_dirs() -> CheckResult:
    problems = []
    for folder in RUNTIME_DIRS:
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            problems.append(f"{folder} ({type(exc).__name__})")
    if problems:
        return CheckResult("Runtime folders", FAIL, "cannot create " + ", ".join(problems))
    return CheckResult("Runtime folders", OK, ", ".join(RUNTIME_DIRS) + " writable")


def check_optional_env() -> CheckResult:
    missing = [label for key, label in OPTIONAL_ENV if key_status(os.getenv(key))[0] != OK]
    if missing:
        return CheckResult("Integrations", WARN, "not configured: " + ", ".join(missing) + " (optional)")
    return CheckResult("Integrations", OK, "all optional integrations configured")


def check_command_routing(config: Any) -> CheckResult:
    """Smoke-test the router without touching the network or launching apps."""
    try:
        from modules.application_manager import ApplicationManager

        manager = ApplicationManager(config)
        probe = manager.process("open up the chrome browser please")
        if not probe.get("success"):
            return CheckResult("Command routing", FAIL, "application module rejected a plain 'open' command")
        cleaned = manager.clean_target("the file explorer")
        if cleaned != "file explorer":
            return CheckResult("Command routing", FAIL, f"app-name cleanup returned {cleaned!r}, expected 'file explorer'")
    except Exception as exc:
        return CheckResult("Command routing", FAIL, f"{type(exc).__name__}: {exc}")
    return CheckResult("Command routing", OK, "'open <app>' reaches the application module")


def run_health_check(verbose: bool = False, writer: Callable[[str], None] = print) -> int:
    """Run every check, print the report, and return a process exit code."""
    writer(_paint("J.A.R.V.I.S V2 self-check", bold=True))
    writer(f"working directory: {Path.cwd()}")
    writer("")

    results: list[CheckResult] = [check_python()]

    config_result, config = check_config()
    results.append(config_result)
    results.append(check_env_file())

    key_result, key = check_groq_key(config)
    results.append(key_result)
    results.append(check_groq_api(key))

    results.extend(check_dependencies())

    if config is not None:
        results.append(check_tts(config))
        results.append(check_command_routing(config))
    results.append(check_audio_playback())
    results.append(check_microphone())
    results.append(check_core_imports())
    results.append(check_runtime_dirs())
    results.append(check_optional_env())

    if not verbose:
        results = [r for r in results if r.level != OK] or results

    for result in results:
        writer(result.render())

    counts = {level: sum(1 for r in results if r.level == level) for level in (OK, WARN, FAIL)}
    writer("")
    summary = f"{counts[OK]} ok, {counts[WARN]} warning(s), {counts[FAIL]} failure(s)"
    if counts[FAIL]:
        writer(_paint(f"NOT READY - {summary}", FAIL, bold=True))
        return 1
    if counts[WARN]:
        writer(_paint(f"READY WITH WARNINGS - {summary}", WARN, bold=True))
        return 0
    writer(_paint(f"ALL GREEN - {summary}", OK, bold=True))
    return 0

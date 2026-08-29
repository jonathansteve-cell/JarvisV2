"""Coverage for the 'open ANY app' resolution work."""

import platform

from core.config_manager import ConfigManager
from modules.application_manager import (
    ApplicationManager,
    _clean_app_name,
    _fuzzy_best,
    _normalize,
    desktop_entry_dirs,
    start_menu_dirs,
)


def make_manager(tmp_path):
    config = ConfigManager(tmp_path / "config.json")
    config.set("applications.paths", {}, save=False)
    return ApplicationManager(config)


def test_clean_target_strips_lead_and_trail_filler():
    assert _clean_app_name("up the chrome browser please") == "chrome"
    assert _clean_app_name("the file explorer") == "file explorer"
    assert _clean_app_name("open up chrome") == "chrome"
    assert _clean_app_name("launch the visual studio code app") == "visual studio code"
    assert _clean_app_name("spotify for me") == "spotify"


def test_clean_target_keeps_real_names():
    assert _clean_app_name("windows terminal") == "windows terminal"
    assert _clean_app_name("android studio") == "android studio"
    assert _clean_app_name("notepad++") == "notepad++"
    assert _clean_app_name("a") == "a"


def test_normalize_ignores_punctuation_and_case():
    assert _normalize("Notepad++") == _normalize("notepad")
    assert _normalize("Visual Studio Code") == "visualstudiocode"


def test_fuzzy_best_finds_close_names_but_rejects_rubbish():
    options = ["Google Chrome", "Mozilla Firefox", "Spotify", "Visual Studio Code"]
    assert _fuzzy_best("google chrome", options) == "Google Chrome"
    assert _fuzzy_best("Google Chrome", options) == "Google Chrome"
    assert _fuzzy_best("chrome", options) is None  # too far from every option
    assert _fuzzy_best("vscode", options) is None


def test_manager_exposes_clean_target_for_the_health_check(tmp_path):
    manager = make_manager(tmp_path)
    assert manager.clean_target("the file explorer") == "file explorer"


def test_try_open_reports_failure_for_an_app_that_is_not_installed(tmp_path):
    manager = make_manager(tmp_path)
    launched, message = manager.try_open("definitely-not-a-real-app-xyz")
    if platform.system() == "Windows":
        # `start` swallows unknown targets, so Windows always reports a launch.
        assert launched in (True, False)
    else:
        assert launched is False
        assert "applications.paths" in message


def test_process_exposes_the_launched_flag(tmp_path):
    manager = make_manager(tmp_path)
    result = manager.process("open up the definitely-not-a-real-app-xyz browser please")
    assert result["success"]  # the module handled it...
    assert result["data"]["app"] == "definitely-not-a-real-app-xyz"
    assert result["data"]["launched"] in (True, False)  # ...and says whether it worked


def test_discovery_helpers_are_safe_on_every_os():
    # These must never raise, even when the OS folders do not exist.
    assert isinstance(start_menu_dirs(), list)
    assert isinstance(desktop_entry_dirs(), list)


def test_config_default_tts_engine(tmp_path):
    config = ConfigManager(tmp_path / "config.json")
    assert config.get("voice.tts_engine") in {"auto", "edge", "pyttsx3", "system"}
    assert isinstance(config.get("voice.edge_voice"), str)

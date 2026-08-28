import platform

import pytest

from core.config_manager import ConfigManager
from modules.application_manager import ApplicationManager, _clean_app_name


def make_manager(tmp_path):
    config = ConfigManager(tmp_path / "config.json")
    config.set("paths.data_dir", str(tmp_path / "data"), save=False)
    config.set("applications.paths", {}, save=False)
    return ApplicationManager(config)


def test_clean_name_strips_filler():
    assert _clean_app_name("chrome browser please") == "chrome"
    assert _clean_app_name("visual studio code app") == "visual studio code"
    assert _clean_app_name("chrome") == "chrome"


def test_config_path_wins(tmp_path):
    fake = tmp_path / "mychrome"
    fake.write_text("#!/bin/sh\nexit 0\n")
    fake.chmod(0o755)
    manager = make_manager(tmp_path)
    manager.config.set("applications.paths", {"chrome": str(fake)}, save=False)
    if platform.system() != "Windows":
        assert "Opening chrome" in manager.open_app("chrome")
    else:
        # On Windows a shell script cannot start; resolver should fall through
        # gracefully rather than crash.
        assert "chrome" in manager.open_app("chrome").lower()


def test_unknown_app_gives_config_hint(tmp_path):
    manager = make_manager(tmp_path)
    response = manager.open_app("definitely-not-a-real-app-xyz")
    assert "applications.paths" in response
    assert "definitely-not-a-real-app-xyz" in response


def test_process_routes_open_command(tmp_path):
    fake = tmp_path / "chromium-fake"
    fake.write_text("#!/bin/sh\nexit 0\n")
    fake.chmod(0o755)
    manager = make_manager(tmp_path)
    manager.config.set("applications.paths", {"chromium-fake": str(fake)}, save=False)
    result = manager.process(f"open {fake.name} browser please")
    assert result["success"]
    assert "Opening" in result["response"]


def test_close_and_list_require_psutil(tmp_path):
    manager = make_manager(tmp_path)
    result = manager.process("close notepad")
    assert result["success"]
    result = manager.process("running apps")
    assert result["success"]

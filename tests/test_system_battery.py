"""Battery questions must get a battery answer, not the CPU/memory line."""

from core.config_manager import ConfigManager
from modules.system_controller import SystemController


def make_controller(tmp_path):
    return SystemController(ConfigManager(tmp_path / "config.json"))


def test_battery_question_is_answered_about_the_battery(tmp_path):
    controller = make_controller(tmp_path)
    answer = controller.describe_battery()
    assert "battery" in answer.lower()
    assert "CPU is at" not in answer


def test_process_routes_battery_before_generic_status(tmp_path):
    controller = make_controller(tmp_path)
    result = controller.process("how much battery is left")
    assert result["success"]
    assert "battery" in result["response"].lower()


def test_process_still_answers_system_status(tmp_path):
    controller = make_controller(tmp_path)
    result = controller.process("system status")
    assert result["success"]
    assert "CPU is at" in result["response"]

"""Task lifecycle commands — added so the CyberHUD can toggle real tasks."""

from core.config_manager import ConfigManager
from modules.productivity_controller import ProductivityController


def make(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    return ProductivityController(cfg)


def test_complete_task_marks_done_and_hides_from_list(tmp_path):
    prod = make(tmp_path)
    prod.process("add task: ship the reactor")

    result = prod.process("complete task ship the reactor")
    assert result["success"]
    assert "marked done" in result["response"].lower()

    listed = prod.process("show tasks")
    assert "no open tasks" in listed["response"].lower()


def test_complete_task_matches_by_substring(tmp_path):
    prod = make(tmp_path)
    prod.process("add task: call mom")

    result = prod.process("finish task mom")
    assert result["success"]
    assert "marked done" in result["response"].lower()


def test_reopen_task_undoes_completion(tmp_path):
    prod = make(tmp_path)
    prod.process("add task: call mom")
    prod.process("complete task call mom")
    assert "no open tasks" in prod.process("show tasks")["response"].lower()

    result = prod.process("reopen task call mom")
    assert "reopened" in result["response"].lower()
    assert "call mom" in prod.process("show tasks")["response"]


def test_delete_task_removes_it_entirely(tmp_path):
    prod = make(tmp_path)
    prod.process("add task: throwaway")

    result = prod.process("delete task throwaway")
    assert "task removed" in result["response"].lower()
    assert prod.data["tasks"] == []


def test_unknown_task_is_reported_not_guessed(tmp_path):
    prod = make(tmp_path)
    prod.process("add task: real task")

    result = prod.process("complete task something else entirely")
    assert result["success"]
    assert "could not find" in result["response"].lower()
    # The real task must survive an unmatched command.
    assert "real task" in prod.process("show tasks")["response"]


def test_complete_task_without_a_name_asks_for_one(tmp_path):
    prod = make(tmp_path)
    result = prod.process("complete task")
    assert "which task" in result["response"].lower()


def test_completed_at_is_stamped_then_cleared(tmp_path):
    prod = make(tmp_path)
    prod.process("add task: stamp me")
    prod.process("complete task stamp me")
    assert prod.data["tasks"][0]["done"] is True
    assert prod.data["tasks"][0]["completed_at"]

    prod.process("reopen task stamp me")
    assert prod.data["tasks"][0]["done"] is False
    assert prod.data["tasks"][0]["completed_at"] is None

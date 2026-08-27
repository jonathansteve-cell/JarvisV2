from core.config_manager import ConfigManager
from modules.productivity_controller import ProductivityController


def test_add_task(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    prod = ProductivityController(cfg)
    response = prod.process("add task: test Jarvis")
    assert response["success"]
    assert "task added" in response["response"].lower()
    listed = prod.process("show tasks")
    assert "test Jarvis" in listed["response"]

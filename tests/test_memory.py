from core.config_manager import ConfigManager
from modules.memory_controller import MemoryController


def test_memory_remember_recall(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    mem = MemoryController(cfg)
    mem.remember("favorite color", "blue")
    facts = mem.recall("color")
    assert facts[0]["value"] == "blue"


def test_memory_learns_name(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    mem = MemoryController(cfg)
    response = mem.learn_from_command("my name is Tony")
    assert "tony" in response.lower()

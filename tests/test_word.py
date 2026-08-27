from core.config_manager import ConfigManager
from modules.word_controller import WordController


def test_word_fallback_or_docx(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.documents_dir", str(tmp_path), save=False)
    word = WordController(cfg)
    created = word.process("create document Test Plan")
    assert created["success"]
    added = word.process("add to document: hello world")
    assert added["success"]
    read = word.process("read document")
    assert "hello world" in read["response"].lower()

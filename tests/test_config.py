from core.config_manager import ConfigManager


def test_config_get_set(tmp_path):
    path = tmp_path / "config.json"
    cfg = ConfigManager(path)
    assert cfg.get("app.name") == "J.A.R.V.I.S V2"
    cfg.set("app.owner_name", "Tony")
    assert cfg.get("app.owner_name") == "Tony"

from core.jarvis import Jarvis


def make_jarvis(tmp_path):
    cfg_path = tmp_path / "config.json"
    jarvis = Jarvis(str(cfg_path), voice_output=False)
    jarvis.config.set("paths.data_dir", str(tmp_path), save=False)
    # Recreate memory-controlled Jarvis would normally need module rewire for data_dir; the default is fine for route tests.
    return jarvis


def test_capabilities_response(tmp_path):
    jarvis = make_jarvis(tmp_path)
    result = jarvis.process_command("what can you do", speak=False)
    assert "control" in result.text.lower() or "applications" in result.text.lower()


def test_power_truth(tmp_path):
    jarvis = make_jarvis(tmp_path)
    result = jarvis.process_command("turn on my PC", speak=False)
    assert "cannot turn on" in result.text.lower()


def test_memory_route(tmp_path):
    jarvis = make_jarvis(tmp_path)
    result = jarvis.process_command("remember favorite movie is iron man", speak=False)
    assert result.success
    assert "remember" in result.text.lower()

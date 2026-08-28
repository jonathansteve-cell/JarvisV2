from core.config_manager import ConfigManager
from modules.roblox_controller import RobloxController


def make_controller(tmp_path) -> RobloxController:
    config = ConfigManager(tmp_path / "config.json")
    config.set("paths.data_dir", str(tmp_path / "data"), save=False)
    return RobloxController(config)


def test_refuses_cheats_and_generators(tmp_path):
    jarvis = make_controller(tmp_path)
    for command in ["use a robux generator for me", "give me an aimbot for roblox", "install a roblox script executor"]:
        result = jarvis.process(command)
        assert result["success"]
        assert "cannot help" in result["response"].lower()
        assert "generator" in result["response"].lower() or "terms" in result["response"].lower()


def test_robux_guidance_is_legit_only(tmp_path):
    jarvis = make_controller(tmp_path)
    result = jarvis.process("hey jarvis, how do I get robux safely?")
    assert result["success"]
    text = result["response"].lower()
    assert "no legitimate robux generator" in text
    assert "premium" in text or "devex" in text or "selling" in text


def test_goal_tracking(tmp_path):
    jarvis = make_controller(tmp_path)
    added = jarvis.process("set roblox goal: finish the obby")
    assert added["success"] and "finish the obby" in added["response"]
    listed = jarvis.process("show roblox goals")
    assert listed["success"] and "finish the obby" in listed["response"]
    done = jarvis.process("complete roblox goal finish the obby")
    assert done["success"] and "complete" in done["response"].lower()


def test_progress_logging_and_stats(tmp_path):
    jarvis = make_controller(tmp_path)
    logged = jarvis.process("log roblox progress: completed daily quests")
    assert logged["success"] and "completed daily quests" in logged["response"]
    stats = jarvis.process("roblox stats")
    assert stats["success"]
    assert "0 grind sessions" in stats["response"] or "sessions logged" in stats["response"]


def test_grind_session_lifecycle(tmp_path):
    jarvis = make_controller(tmp_path)
    started = jarvis.process("start 30 minute roblox grind session for daily quests")
    assert started["success"] and "30 minutes" in started["response"] and "daily quests" in started["response"]
    status = jarvis.process("roblox grind status")
    assert status["success"] and "active" in status["response"].lower()
    ended = jarvis.process("end grind session")
    assert ended["success"] and "logged" in ended["response"].lower()
    again = jarvis.process("roblox stats")
    assert again["success"] and "1 grind session" in again["response"]


def test_link_commands(tmp_path):
    jarvis = make_controller(tmp_path)
    result = jarvis.process("open robux page")
    assert result["success"] and "robux" in result["response"].lower()
    result = jarvis.process("open roblox creator hub")
    assert result["success"] and "creator hub" in result["response"].lower()


def test_ignores_unrelated_commands(tmp_path):
    jarvis = make_controller(tmp_path)
    result = jarvis.process("what is the weather today")
    assert not result["success"]

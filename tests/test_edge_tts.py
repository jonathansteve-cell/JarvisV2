"""The edge-tts path must work when it can and fall back silently when it cannot.

These tests stub the network so the shipped code path actually runs.
"""

import sys
import types
from pathlib import Path

import pytest

from core.config_manager import ConfigManager
from voice.text_to_speech import TextToSpeech, find_audio_player


class FakeCommunicate:
    """Stands in for edge_tts.Communicate."""

    payload = b"ID3-fake-audio"
    raises: Exception | None = None
    saved_to: list[str] = []
    used_voice: list[str] = []
    used_rate: list[str] = []

    def __init__(self, text, voice, rate="+0%"):
        self.text = text
        self.voice = voice
        self.rate = rate

    async def save(self, path):
        FakeCommunicate.used_voice.append(self.voice)
        FakeCommunicate.used_rate.append(self.rate)
        if FakeCommunicate.raises:
            raise FakeCommunicate.raises
        Path(path).write_bytes(FakeCommunicate.payload)
        FakeCommunicate.saved_to.append(path)


@pytest.fixture
def fake_edge_tts(monkeypatch):
    FakeCommunicate.payload = b"ID3-fake-audio"
    FakeCommunicate.saved_to = []
    FakeCommunicate.used_voice = []
    FakeCommunicate.used_rate = []
    FakeCommunicate.raises = None
    module = types.ModuleType("edge_tts")
    module.Communicate = FakeCommunicate
    monkeypatch.setitem(sys.modules, "edge_tts", module)
    return module


@pytest.fixture
def tts(tmp_path):
    config = ConfigManager(tmp_path / "config.json")
    config.set("voice.tts_engine", "edge", save=False)
    engine = TextToSpeech(config)
    engine._engine = None  # force the non-pyttsx3 branch
    engine._edge_available = True
    return engine


def test_find_audio_player_shape():
    player = find_audio_player()
    assert player is None or (isinstance(player[0], str) and isinstance(player[1], list))


def test_edge_synthesis_and_cleanup(tts, fake_edge_tts, monkeypatch):
    played: list[Path] = []
    contents: list[bytes] = []

    def fake_play(path):
        # Read while the file still exists: playback happens before cleanup.
        played.append(path)
        contents.append(Path(path).read_bytes())
        return True

    monkeypatch.setattr(tts, "_play_file", fake_play)

    assert tts._speak_edge("Systems online, sir.") is True
    assert len(played) == 1
    assert played[0].suffix == ".mp3"
    assert contents == [FakeCommunicate.payload]
    assert not played[0].exists()  # temp file cleaned up afterwards
    assert FakeCommunicate.used_voice == [tts.edge_voice]


def test_edge_rate_follows_the_profile_rate(tts, fake_edge_tts, monkeypatch):
    monkeypatch.setattr(tts, "_play_file", lambda path: True)
    tts.config.set("voice.tts_rate", 178, save=False)
    tts._speak_edge("normal")
    assert FakeCommunicate.used_rate == ["+0%"]

    tts.config.set("voice.tts_rate", 223, save=False)
    tts._speak_edge("faster")
    assert FakeCommunicate.used_rate[-1] == "+25%"

    tts.config.set("voice.tts_rate", 89, save=False)
    tts._speak_edge("slower")
    assert FakeCommunicate.used_rate[-1] == "-50%"


def test_edge_synthesis_failure_falls_back_without_raising(tts, fake_edge_tts):
    FakeCommunicate.raises = RuntimeError("no route to speech.platform.bing.com")
    assert tts._speak_edge("Systems online, sir.") is False
    assert "edge-tts synthesis failed" in tts._last_error


def test_empty_audio_file_counts_as_failure(tts, fake_edge_tts, monkeypatch):
    FakeCommunicate.payload = b""
    monkeypatch.setattr(tts, "_play_file", lambda path: True)
    assert tts._speak_edge("Systems online, sir.") is False


def test_playback_failure_falls_back(tts, fake_edge_tts, monkeypatch):
    monkeypatch.setattr(tts, "_play_file", lambda path: False)
    assert tts._speak_edge("Systems online, sir.") is False


def test_speak_now_uses_edge_then_falls_back(tts, fake_edge_tts, monkeypatch):
    calls = []
    monkeypatch.setattr(tts, "_speak_edge", lambda text: calls.append(text) and False)
    monkeypatch.setattr(tts, "_os_fallback", lambda text: calls.append(("os", text)))

    tts._speak_now("hello")
    assert calls[0] == "hello"
    assert calls[1] == ("os", "hello")


def test_pyttsx3_engine_preference_still_wins(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "edge_tts", None)  # not installed
    config = ConfigManager(tmp_path / "config.json")
    config.set("voice.tts_engine", "pyttsx3", save=False)
    engine = TextToSpeech(config)
    engine._engine = None
    engine._edge_available = False
    assert engine.describe_engine()["backend"] == "none"


def test_describe_engine_reports_edge(tmp_path, monkeypatch):
    config = ConfigManager(tmp_path / "config.json")
    config.set("voice.tts_engine", "edge", save=False)
    config.set("voice.edge_voice", "en-GB-RyanNeural", save=False)
    engine = TextToSpeech(config)
    engine._engine = None
    monkeypatch.setattr(engine, "_edge_importable", lambda: True)
    report = engine.describe_engine()
    assert report["backend"] == "edge"
    assert report["voice"] == "en-GB-RyanNeural"


def test_profile_picks_a_neural_voice(tmp_path):
    config = ConfigManager(tmp_path / "config.json")
    config.set("voice.tts_engine", "edge", save=False)
    config.set("voice.edge_voice", "", save=False)
    engine = TextToSpeech(config)
    assert engine.edge_voice.endswith("Neural")

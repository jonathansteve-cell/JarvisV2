"""Home Assistant must actually be called, not silently simulated."""

import pytest

from core.config_manager import ConfigManager
from modules import smart_home_controller
from modules.smart_home_controller import SmartHomeController, _entity_for


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None


class FakeRequests:
    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "json": json})
        if self.fail:
            raise ConnectionError("home assistant unreachable")
        return FakeResponse()


@pytest.fixture
def controller(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    return SmartHomeController(cfg)


def test_entity_mapping():
    assert _entity_for("living room light") == ("light", "living_room_light")
    assert _entity_for("thermostat") == ("climate", "thermostat")
    assert _entity_for("front door") == ("lock", "front_door")
    assert _entity_for("ceiling fan") == ("fan", "ceiling_fan")


def test_home_assistant_is_called_when_configured(controller, monkeypatch):
    fake = FakeRequests()
    monkeypatch.setattr(smart_home_controller, "requests", fake)
    monkeypatch.setenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
    monkeypatch.setenv("HOME_ASSISTANT_TOKEN", "long-lived-token")

    result = controller.process("turn on living room light")

    assert result["success"]
    assert len(fake.calls) == 1, "the Home Assistant API was never called"
    assert fake.calls[0]["url"].endswith("/api/services/light/turn_on")
    assert fake.calls[0]["json"] == {"entity_id": "light.living_room_light"}
    assert "Home Assistant" in result["response"]
    assert "simulated" not in result["response"]


def test_thermostat_sends_a_temperature(controller, monkeypatch):
    fake = FakeRequests()
    monkeypatch.setattr(smart_home_controller, "requests", fake)
    monkeypatch.setenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
    monkeypatch.setenv("HOME_ASSISTANT_TOKEN", "token")

    controller.process("set thermostat to 21")

    assert fake.calls[0]["url"].endswith("/api/services/climate/set_temperature")
    assert fake.calls[0]["json"] == {"entity_id": "climate.thermostat", "temperature": 21}


def test_door_lock_uses_the_lock_domain(controller, monkeypatch):
    fake = FakeRequests()
    monkeypatch.setattr(smart_home_controller, "requests", fake)
    monkeypatch.setenv("HOME_ASSISTANT_URL", "http://h")
    monkeypatch.setenv("HOME_ASSISTANT_TOKEN", "t")

    controller.process("unlock door")
    assert fake.calls[0]["url"].endswith("/api/services/lock/unlock")


def test_a_failing_home_assistant_falls_back_to_simulation(controller, monkeypatch):
    fake = FakeRequests(fail=True)
    monkeypatch.setattr(smart_home_controller, "requests", fake)
    monkeypatch.setenv("HOME_ASSISTANT_URL", "http://unreachable")
    monkeypatch.setenv("HOME_ASSISTANT_TOKEN", "t")

    result = controller.process("turn off bedroom light")
    assert result["success"]
    assert "simulated" in result["response"]
    assert controller.state["bedroom light"] == "off"  # local copy still updated


def test_without_credentials_it_still_answers_and_admits_it(controller, monkeypatch):
    monkeypatch.delenv("HOME_ASSISTANT_URL", raising=False)
    monkeypatch.delenv("HOME_ASSISTANT_TOKEN", raising=False)

    result = controller.process("turn on living room light")
    assert result["success"]
    assert "simulated" in result["response"]


def test_status_reports_which_mode_is_live(controller, monkeypatch):
    monkeypatch.setenv("HOME_ASSISTANT_URL", "http://h")
    monkeypatch.setenv("HOME_ASSISTANT_TOKEN", "t")
    live = controller.process("smart home status")
    assert "Home Assistant" in live["response"]
    assert live["data"]["mode"] == "Home Assistant"

    monkeypatch.delenv("HOME_ASSISTANT_TOKEN", raising=False)
    assert "local simulation" in controller.process("smart home status")["response"]


def test_local_state_persists(controller, tmp_path):
    controller.process("turn on living room light")
    assert "living room light" in controller.path.read_text(encoding="utf-8")

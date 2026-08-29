"""Phone calling: dial when a TwiML URL exists, otherwise say why it can't."""

import sys
import types

import pytest

from core.config_manager import ConfigManager
from modules import phone_controller
from modules.phone_controller import PhoneController


class FakeCall:
    sid = "CA_fake_sid_123"


class FakeCalls:
    def __init__(self, fail=False):
        self.created = []
        self.fail = fail

    def create(self, to=None, from_=None, url=None):
        self.created.append({"to": to, "from_": from_, "url": url})
        if self.fail:
            raise RuntimeError("Twilio rejected the call")
        return FakeCall()


class FakeClient:
    last = None

    def __init__(self, sid, token):
        self.calls = FakeClient.last


@pytest.fixture
def phone(tmp_path, monkeypatch):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    controller = PhoneController(cfg)
    opened = []
    monkeypatch.setattr(phone_controller.webbrowser, "open", opened.append)
    controller.opened = opened
    return controller


def install_twilio(monkeypatch, fail=False):
    FakeCalls.last = FakeCalls(fail=fail)
    FakeClient.last = FakeCalls.last
    rest = types.ModuleType("twilio.rest")
    rest.Client = FakeClient
    pkg = types.ModuleType("twilio")
    pkg.rest = rest
    monkeypatch.setitem(sys.modules, "twilio", pkg)
    monkeypatch.setitem(sys.modules, "twilio.rest", rest)
    return FakeCalls.last


def test_it_actually_dials_when_twiml_is_present(phone, monkeypatch):
    calls = install_twilio(monkeypatch)
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACxxxx")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_PHONE", "+15550001111")
    monkeypatch.setenv("TWILIO_TWIML_URL", "https://handler.twilio.com/twiml/abc")

    result = phone.process("call +15551234567")

    assert result["success"]
    assert len(calls.created) == 1, "Twilio was never asked to place the call"
    assert calls.created[0]["to"] == "+15551234567"
    assert calls.created[0]["url"] == "https://handler.twilio.com/twiml/abc"
    assert "CA_fake_sid_123" in result["response"]


def test_twiml_can_come_from_config_too(phone, monkeypatch):
    calls = install_twilio(monkeypatch)
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACxxxx")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_PHONE", "+15550001111")
    monkeypatch.delenv("TWILIO_TWIML_URL", raising=False)
    phone.config.set("integrations.phone.twiml_url", "https://example.com/twiml", save=False)

    phone.process("call +15551234567")
    assert calls.created[0]["url"] == "https://example.com/twiml"


def test_configured_but_no_twiml_explains_itself(phone, monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACxxxx")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_PHONE", "+15550001111")
    monkeypatch.delenv("TWILIO_TWIML_URL", raising=False)

    result = phone.process("call +15551234567")
    assert "TWILIO_TWIML_URL" in result["response"]
    assert phone.opened == ["tel:+15551234567"]


def test_twilio_failure_is_reported_not_swallowed(phone, monkeypatch):
    install_twilio(monkeypatch, fail=True)
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACxxxx")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_PHONE", "+15550001111")
    monkeypatch.setenv("TWILIO_TWIML_URL", "https://example.com/twiml")

    result = phone.process("call +15551234567")
    assert "Twilio could not place the call" in result["response"]


def test_no_twilio_at_all_opens_the_dialer(phone, monkeypatch):
    for key in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_PHONE", "TWILIO_TWIML_URL"):
        monkeypatch.delenv(key, raising=False)
    result = phone.process("call 0400111222")
    assert "dialer" in result["response"]
    assert phone.opened == ["tel:0400111222"]


def test_video_calls_are_not_hijacked(phone):
    assert phone.process("join zoom video call")["success"] is False

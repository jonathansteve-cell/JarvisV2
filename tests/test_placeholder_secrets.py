"""A fresh .env must not count as 'configured' — that is how integrations end up
claiming to be live while every call silently fails."""


from core.config_manager import ConfigManager
from modules.email_controller import EmailController
from modules.phone_controller import PhoneController
from modules.smart_home_controller import SmartHomeController
from utils.helpers import is_placeholder_secret


def test_the_shipped_template_values_are_all_placeholders():
    for value in (
        "Your_real_API_key",
        "your_groq_api_key_here",
        "your_email_app_password_here",
        "your_twilio_sid_here",
        "your_home_assistant_long_lived_token_here",
        "your_spotify_client_id_here",
    ):
        assert is_placeholder_secret(value), value


def test_missing_is_a_placeholder_too():
    assert is_placeholder_secret(None)
    assert is_placeholder_secret("")
    assert is_placeholder_secret("   ")


def test_a_real_value_is_not():
    assert not is_placeholder_secret("gsk_" + "a" * 40)
    assert not is_placeholder_secret("http://homeassistant.local:8123")


def test_email_is_not_configured_on_a_fresh_env(monkeypatch):
    monkeypatch.setenv("JARVIS_EMAIL_ADDRESS", "you@example.com")
    monkeypatch.setenv("JARVIS_EMAIL_APP_PASSWORD", "your_email_app_password_here")
    assert EmailController(ConfigManager("config/config.json")).configured() is False

    monkeypatch.setenv("JARVIS_EMAIL_APP_PASSWORD", "abcd efgh ijkl mnop")
    assert EmailController(ConfigManager("config/config.json")).configured() is True


def test_smart_home_is_not_configured_on_a_fresh_env(monkeypatch):
    monkeypatch.setenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
    monkeypatch.setenv("HOME_ASSISTANT_TOKEN", "your_home_assistant_long_lived_token_here")
    controller = SmartHomeController(ConfigManager("config/config.json"))
    assert controller.configured() is False
    assert controller.mode() == "local simulation"
    assert "local simulation" in controller.process("smart home status")["response"]


def test_smart_home_admits_when_a_real_token_still_fails(monkeypatch):
    monkeypatch.setenv("HOME_ASSISTANT_URL", "http://unreachable.invalid:8123")
    monkeypatch.setenv("HOME_ASSISTANT_TOKEN", "a-real-looking-token-value")
    controller = SmartHomeController(ConfigManager("config/config.json"))
    assert controller.configured() is True

    controller.process("turn on living room light")  # will fail to connect
    assert controller.mode() == "Home Assistant configured but unreachable - simulating"
    assert "unreachable" in controller.process("smart home status")["response"]


def test_phone_is_not_configured_on_a_fresh_env(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "your_twilio_sid_here")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "your_twilio_auth_token_here")
    monkeypatch.setenv("TWILIO_FROM_PHONE", "+15551234567")
    monkeypatch.setenv("TWILIO_TWIML_URL", "")
    controller = PhoneController(ConfigManager("config/config.json"))
    assert controller.configured() is False

    # The user must get the honest "no credentials" message, not "Twilio is configured".
    import webbrowser

    opened = []
    monkeypatch.setattr(webbrowser, "open", opened.append)
    response = controller.process("call +15559876543")["response"]
    assert "TWILIO_TWIML_URL" not in response
    assert "dialer" in response



from utils.health_check import (
    FAIL,
    OK,
    WARN,
    check_groq_api,
    check_groq_key,
    check_python,
    key_status,
    run_health_check,
)


def test_key_status_detects_the_template_placeholder():
    # This is exactly what .env ships with, so a forgotten rotation must be loud.
    level, detail = key_status("Your_real_API_key")
    assert level == FAIL
    assert "placeholder" in detail


def test_key_status_detects_missing_and_short_keys():
    assert key_status(None)[0] == FAIL
    assert key_status("   ")[0] == FAIL
    level, detail = key_status("gsk_tooshort")
    assert level == WARN
    assert "short" in detail


def test_key_status_accepts_a_real_looking_key_without_echoing_it():
    fake = "gsk_" + "a" * 48 + "9Zx4"
    level, detail = key_status(fake)
    assert level == OK
    assert "9Zx4" in detail  # last four only
    assert fake not in detail  # the key itself must never be printed
    assert "a" * 10 not in detail


def test_check_python_passes_on_the_interpreter_running_the_tests():
    result = check_python()
    assert result.level == OK


def test_run_health_check_reports_and_hides_the_key(monkeypatch, capsys):
    monkeypatch.setenv("GROQ_API_KEY", "Your_real_API_key")
    lines = []
    code = run_health_check(verbose=True, writer=lines.append)

    assert isinstance(code, int)
    report = "\n".join(lines)

    # The placeholder key must be flagged, never echoed.
    assert "GROQ_API_KEY" in report
    assert "placeholder" in report
    assert "Your_real_API_key" not in report

    # Every section of the report is present.
    for section in ("Python", "Config", "Groq API", "Speech output", "Command routing"):
        assert section in report


def test_run_health_check_fails_on_a_placeholder_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "Your_real_API_key")
    assert run_health_check(writer=lambda _line: None) == 1


def test_placeholder_key_is_not_sent_to_the_api(monkeypatch):
    """Regression: probing with the shipped template produced a bogus error."""
    monkeypatch.setenv("GROQ_API_KEY", "Your_real_API_key")
    result, usable = check_groq_key(None)
    assert result.level == FAIL
    assert usable is None
    assert "skipped" in check_groq_api(usable).message


def test_real_looking_key_is_passed_to_the_api_probe(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_" + "b" * 48 + "7Qw2")
    _result, usable = check_groq_key(None)
    assert usable is not None
    assert usable.endswith("7Qw2")


def test_offline_probe_is_a_warning_not_a_failure(monkeypatch):
    import requests

    class _Offline(Exception):
        pass

    def _boom(*_args, **_kwargs):
        raise _Offline("no route to host")

    monkeypatch.setattr(requests, "get", _boom, raising=False)
    result = check_groq_api("gsk_" + "c" * 48 + "3Lm8")
    assert result.level == WARN
    assert "could not reach" in result.message


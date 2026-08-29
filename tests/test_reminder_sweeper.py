"""Reminders must actually fire, not just sit in a JSON file."""

import json
import threading
from datetime import datetime, timedelta

from core.config_manager import ConfigManager
from modules.productivity_controller import ProductivityController


def make(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    return ProductivityController(cfg)


def test_reminder_with_a_time_is_stored_with_a_time(tmp_path):
    prod = make(tmp_path)
    response = prod.process("remind me to call mom at 6pm")
    assert response["success"]
    stored = prod.data["reminders"][-1]
    assert stored["due_at"] is not None  # the regression: this used to be None
    assert "Reminder set for" in response["response"]


def test_reminder_without_a_parseable_time_says_so(tmp_path):
    prod = make(tmp_path)
    response = prod.process("remind me to buy milk sometime")
    assert stored_due_is_none(prod)
    assert "could not work out when" in response["response"]


def stored_due_is_none(prod):
    return prod.data["reminders"][-1]["due_at"] is None


def test_due_reminders_only_returns_overdue_items(tmp_path):
    prod = make(tmp_path)
    prod.add_reminder("past thing", datetime.now() - timedelta(minutes=5))
    prod.add_reminder("future thing", datetime.now() + timedelta(hours=1))
    prod.add_reminder("no time thing", None)

    due = prod.due_reminders()
    assert [item["text"] for item in due] == ["past thing"]


def test_sweep_due_notifies_and_fires_only_once(tmp_path):
    prod = make(tmp_path)
    heard = []
    prod.start_notifier(heard.append, interval=999)  # thread stays idle; we sweep by hand

    prod.add_reminder("stand up", datetime.now() - timedelta(minutes=1))
    assert prod.sweep_due() == ["stand up"]
    assert heard == ["stand up"]

    # Second pass must not re-fire it.
    assert prod.sweep_due() == []
    assert heard == ["stand up"]
    assert prod.data["reminders"][-1]["done"] is True
    prod.stop_notifier()


def test_swept_reminder_is_persisted_as_done(tmp_path):
    prod = make(tmp_path)
    prod.start_notifier(lambda _text: None, interval=999)
    prod.add_reminder("pay bill", datetime.now() - timedelta(seconds=1))
    prod.sweep_due()
    prod.stop_notifier()

    on_disk = json.loads(prod.path.read_text(encoding="utf-8"))
    assert on_disk["reminders"][-1]["done"] is True
    assert on_disk["reminders"][-1]["fired_at"]


def test_the_notifier_thread_fires_on_its_own(tmp_path):
    prod = make(tmp_path)
    heard = []
    ready = threading.Event()

    def callback(text):
        heard.append(text)
        ready.set()

    prod.add_reminder("drink water", datetime.now() - timedelta(seconds=1))
    prod.start_notifier(callback, interval=0.05)

    assert ready.wait(timeout=5), "the background sweeper never fired"
    assert heard == ["drink water"]
    prod.stop_notifier()


def test_a_failing_callback_does_not_kill_the_sweeper(tmp_path):
    prod = make(tmp_path)

    def boom(_text):
        raise RuntimeError("tts exploded")

    prod.start_notifier(boom, interval=999)
    prod.add_reminder("still logged", datetime.now() - timedelta(seconds=1))
    assert prod.sweep_due() == ["still logged"]  # marked done despite the exception
    assert prod.data["reminders"][-1]["done"] is True
    prod.stop_notifier()


def test_due_reminders_command(tmp_path):
    prod = make(tmp_path)
    prod.start_notifier(lambda _text: None, interval=999)
    prod.add_reminder("stretch", datetime.now() - timedelta(seconds=1))
    response = prod.process("any reminders due")
    assert "stretch" in response["response"]
    assert prod.process("any reminders due")["response"] == "Nothing is due right now, sir."
    prod.stop_notifier()


def test_timer_callback_is_invoked(tmp_path):
    prod = make(tmp_path)
    heard = []
    prod.start_notifier(heard.append, interval=999)
    prod.set_timer(0, "eggs")
    import time

    for _ in range(100):
        if heard:
            break
        time.sleep(0.02)
    assert heard == ["eggs"]
    prod.stop_notifier()

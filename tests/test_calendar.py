"""Calendar events must use the time the user actually said."""

from datetime import datetime, timedelta

from core.config_manager import ConfigManager
from modules.calendar_controller import CalendarController


def make(tmp_path):
    cfg = ConfigManager(tmp_path / "config.json")
    cfg.set("paths.data_dir", str(tmp_path), save=False)
    return CalendarController(cfg)


def test_a_stated_time_is_used(tmp_path):
    cal = make(tmp_path)
    response = cal.add_event("dentist appointment", "tomorrow at 6pm")
    start = datetime.fromisoformat(cal.events[-1]["start"])
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    assert start.date() == tomorrow
    assert (start.hour, start.minute) == (18, 0)
    assert "6:00 PM" in response or "6:00" in response


def test_relative_time_is_used(tmp_path):
    cal = make(tmp_path)
    cal.add_event("stand up", "in 30 minutes")
    start = datetime.fromisoformat(cal.events[-1]["start"])
    delta = (start - datetime.now()).total_seconds()
    assert 28 * 60 < delta < 31 * 60


def test_unparseable_time_says_so_instead_of_pretending(tmp_path):
    cal = make(tmp_path)
    response = cal.add_event("mystery meeting", "whenever")
    assert "could not read a time" in response
    # It still files the event rather than dropping it.
    assert cal.events[-1]["title"] == "mystery meeting"


def test_list_events_shows_times_and_sorts(tmp_path):
    cal = make(tmp_path)
    cal.add_event("later thing", "in 3 hours")
    cal.add_event("sooner thing", "in 10 minutes")
    listing = cal.list_events()
    assert "sooner thing" in listing and "later thing" in listing
    assert listing.index("sooner thing") < listing.index("later thing")


def test_process_routes_an_add_with_a_time(tmp_path):
    cal = make(tmp_path)
    result = cal.process("add calendar event: dentist tomorrow at 6pm")
    assert result["success"]
    start = datetime.fromisoformat(cal.events[-1]["start"])
    assert start.hour == 18


def test_empty_calendar(tmp_path):
    assert "no events" in make(tmp_path).list_events()

"""Absolute and relative time parsing for reminders and calendar events."""

from datetime import datetime

from utils.helpers import parse_delay

NOW = datetime(2026, 8, 29, 10, 0, 0)


def test_relative_phrases_still_work():
    assert parse_delay("in 10 minutes", NOW) == datetime(2026, 8, 29, 10, 10)
    assert parse_delay("in 2 hours", NOW) == datetime(2026, 8, 29, 12, 0)
    assert parse_delay("in 3 days", NOW) == datetime(2026, 9, 1, 10, 0)
    assert parse_delay("in 45 seconds", NOW) == datetime(2026, 8, 29, 10, 0, 45)
    assert parse_delay("in 1 week", NOW) == datetime(2026, 9, 5, 10, 0)


def test_clock_times_are_parsed():
    assert parse_delay("remind me to call mom at 6pm", NOW) == datetime(2026, 8, 29, 18, 0)
    assert parse_delay("at 6:30 pm", NOW) == datetime(2026, 8, 29, 18, 30)
    assert parse_delay("at 9am", NOW) == datetime(2026, 8, 30, 9, 0)  # 9am is past, so tomorrow
    assert parse_delay("at 18:30", NOW) == datetime(2026, 8, 29, 18, 30)


def test_a_time_already_gone_today_rolls_to_tomorrow():
    assert parse_delay("at 8am", NOW) == datetime(2026, 8, 30, 8, 0)


def test_bare_hour_reads_as_evening():
    # "remind me at 6" means 6pm, not 6am.
    assert parse_delay("at 6", NOW) == datetime(2026, 8, 29, 18, 0)
    # 8 and above are taken literally.
    assert parse_delay("at 11", NOW) == datetime(2026, 8, 29, 11, 0)


def test_tomorrow():
    assert parse_delay("tomorrow at 6pm", NOW) == datetime(2026, 8, 30, 18, 0)
    assert parse_delay("remind me tomorrow", NOW) == datetime(2026, 8, 30, 9, 0)


def test_midnight_edge_cases():
    assert parse_delay("at 12am", NOW) == datetime(2026, 8, 30, 0, 0)
    assert parse_delay("at 12pm", NOW) == datetime(2026, 8, 29, 12, 0)


def test_nonsense_returns_none():
    assert parse_delay("sometime soon", NOW) is None
    assert parse_delay("", NOW) is None
    assert parse_delay("at 99:99", NOW) is None

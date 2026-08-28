"""Voice persona profiles for Jarvis V2 text-to-speech.

Profiles tune rate, volume, pitch, and preferred system voices so the assistant
can sound calm and professional or deep and dark-synthetic. The ``dark_synthetic``
profile is an ORIGINAL heavy synthetic persona (slower, lower, more commanding).
It is not a clone or impersonation of any film character or real person.
"""

from __future__ import annotations

from typing import Any

DEFAULT_PROFILE = "dark_synthetic"

VOICE_PROFILES: dict[str, dict[str, Any]] = {
    "dark_synthetic": {
        "description": (
            "Original dark synthetic persona: slow, low, heavy, and commanding. "
            "Closest available vibe to a cinematic villain AI without copying anyone."
        ),
        "rate": 148,
        "volume": 1.0,
        "pitch": 15,
        "gender": "male",
        "hints": ["david", "male", "george", "guy", "en-gb", "english"],
    },
    "jarvis_classic": {
        "description": "Calm, polite, professional butler-style assistant voice.",
        "rate": 180,
        "volume": 0.9,
        "pitch": 52,
        "gender": "male",
        "hints": ["george", "en-gb", "british", "guy", "david", "male"],
    },
    "fast_operator": {
        "description": "Brisk, mission-control pace for rapid command acknodgement.",
        "rate": 215,
        "volume": 0.95,
        "pitch": 55,
        "gender": "male",
        "hints": ["male", "david", "mark", "george"],
    },
    "gentle": {
        "description": "Softer, quieter voice for late-night sessions.",
        "rate": 168,
        "volume": 0.75,
        "pitch": 60,
        "gender": "female",
        "hints": ["zira", "female", "susan", "samantha"],
    },
}

_FALLBACK: dict[str, Any] = {
    "description": "Neutral default profile.",
    "rate": 178,
    "volume": 0.9,
    "pitch": 50,
    "gender": "male",
    "hints": [],
}


def profile_names() -> list[str]:
    """Return all available profile names."""
    return sorted(VOICE_PROFILES)


def get_profile(name: str | None) -> dict[str, Any]:
    """Resolve a profile by name, falling back to the default profile."""
    key = (name or DEFAULT_PROFILE).strip().lower()
    if key in VOICE_PROFILES:
        return dict(VOICE_PROFILES[key])
    return dict(VOICE_PROFILES.get(DEFAULT_PROFILE, _FALLBACK))

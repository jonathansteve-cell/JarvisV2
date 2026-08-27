"""Spotify music control."""

from __future__ import annotations

import os
import re
import urllib.parse
import webbrowser
from typing import Any


class SpotifyController:
    """Control Spotify Web API when configured, with web fallback."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self._client = None

    def _spotify(self):
        if self._client:
            return self._client
        if not (os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")):
            return None
        try:
            import spotipy  # type: ignore
            from spotipy.oauth2 import SpotifyOAuth  # type: ignore

            scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
            self._client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
            return self._client
        except Exception:
            return None

    def play(self, query: str = "") -> str:
        sp = self._spotify()
        if sp:
            try:
                if query:
                    results = sp.search(q=query, type="track", limit=1)
                    items = results.get("tracks", {}).get("items", [])
                    if items:
                        sp.start_playback(uris=[items[0]["uri"]])
                        return f"Playing {items[0]['name']} by {items[0]['artists'][0]['name']}, sir."
                sp.start_playback()
                return "Spotify playback started, sir."
            except Exception as exc:
                return f"Spotify playback failed: {exc}"
        if query:
            webbrowser.open("https://open.spotify.com/search/" + urllib.parse.quote(query))
            return f"Opening Spotify search for {query}, sir."
        webbrowser.open("https://open.spotify.com")
        return "Opening Spotify, sir."

    def pause(self) -> str:
        sp = self._spotify()
        if sp:
            try:
                sp.pause_playback()
                return "Spotify paused, sir."
            except Exception as exc:
                return f"Spotify pause failed: {exc}"
        return "Spotify API is not configured, sir."

    def next_track(self) -> str:
        sp = self._spotify()
        if sp:
            try:
                sp.next_track()
                return "Skipping to the next track, sir."
            except Exception as exc:
                return f"Spotify skip failed: {exc}"
        return "Spotify API is not configured, sir."

    def current(self) -> str:
        sp = self._spotify()
        if sp:
            try:
                item = sp.current_user_playing_track()
                if item and item.get("item"):
                    track = item["item"]
                    return f"Now playing {track['name']} by {track['artists'][0]['name']}, sir."
                return "Spotify is not currently playing anything, sir."
            except Exception as exc:
                return f"Spotify status failed: {exc}"
        return "Spotify API is not configured, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        if "spotify" not in lower and not any(x in lower for x in ["play song", "pause music", "next song", "now playing"]):
            return {"success": False, "response": "I did not find a Spotify command, sir."}
        play_match = re.search(r"play(?: song| spotify)? (.+)", command, re.I)
        if play_match:
            return {"success": True, "response": self.play(play_match.group(1).strip())}
        if "pause" in lower:
            return {"success": True, "response": self.pause()}
        if "next" in lower or "skip" in lower:
            return {"success": True, "response": self.next_track()}
        if "now playing" in lower or "current song" in lower:
            return {"success": True, "response": self.current()}
        if "open spotify" in lower:
            return {"success": True, "response": self.play()}
        return {"success": False, "response": "I did not find a Spotify command, sir."}

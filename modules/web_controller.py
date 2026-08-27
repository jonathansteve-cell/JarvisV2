"""Web and information commands."""

from __future__ import annotations

import re
import urllib.parse
import webbrowser
from typing import Any


SITES = {
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "google": "https://google.com",
    "calendar": "https://calendar.google.com",
    "spotify": "https://open.spotify.com",
    "chatgpt": "https://chat.openai.com",
}


class WebController:
    """Open websites and route web searches."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def open_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        if not self.config.get("behavior.allow_web_open", True):
            return "Web opening is disabled in configuration, sir."
        webbrowser.open(url)
        return f"Opening {url}, sir."

    def search_google(self, query: str) -> str:
        encoded = urllib.parse.quote_plus(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        return f"Searching Google for {query}, sir."

    def wikipedia(self, query: str) -> str:
        try:
            import wikipedia  # type: ignore

            return wikipedia.summary(query, sentences=2)
        except Exception:
            webbrowser.open("https://en.wikipedia.org/wiki/" + urllib.parse.quote(query.replace(" ", "_")))
            return f"Opening Wikipedia results for {query}, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        search_match = re.search(r"(?:google|search(?: google)? for) (.+)", command, re.I)
        if search_match:
            return {"success": True, "response": self.search_google(search_match.group(1).strip())}
        wiki_match = re.search(r"(?:wikipedia|who is|what is) (.+)", command, re.I)
        if wiki_match and not lower.startswith("what is running"):
            return {"success": True, "response": self.wikipedia(wiki_match.group(1).strip())}
        if "weather" in lower:
            return {"success": True, "response": self.search_google("weather near me")}
        if "news" in lower:
            return {"success": True, "response": self.open_url("https://news.google.com")}
        for name, url in SITES.items():
            if f"open {name}" in lower:
                return {"success": True, "response": self.open_url(url)}
        url_match = re.search(r"open (https?://\S+|[\w.-]+\.[a-z]{2,}(?:/\S*)?)", lower)
        if url_match:
            return {"success": True, "response": self.open_url(url_match.group(1))}
        return {"success": False, "response": "I did not find a web command, sir."}

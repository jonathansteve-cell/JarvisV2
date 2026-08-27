"""Social media posting integrations."""

from __future__ import annotations

import os
import re
import webbrowser
from typing import Any


class SocialMediaController:
    """Post to social platforms when API credentials are configured."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def tweet(self, text: str) -> str:
        if all(os.getenv(k) for k in ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"]):
            try:
                import tweepy  # type: ignore

                client = tweepy.Client(
                    consumer_key=os.getenv("TWITTER_API_KEY"),
                    consumer_secret=os.getenv("TWITTER_API_SECRET"),
                    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
                )
                client.create_tweet(text=text)
                return "Tweet posted, sir."
            except Exception as exc:
                return f"Twitter posting failed: {exc}"
        webbrowser.open("https://twitter.com/intent/tweet?text=" + text.replace(" ", "%20"))
        return "Opening Twitter with the post prepared, sir."

    def linkedin(self, text: str) -> str:
        webbrowser.open("https://www.linkedin.com/feed/")
        return "Opening LinkedIn. API posting requires a LinkedIn developer app, sir."

    def process(self, command: str) -> dict[str, Any]:
        tweet_match = re.search(r"(?:tweet|post to twitter)[: ]+(.+)", command, re.I | re.S)
        if tweet_match:
            return {"success": True, "response": self.tweet(tweet_match.group(1).strip())}
        linkedin_match = re.search(r"post to linkedin[: ]+(.+)", command, re.I | re.S)
        if linkedin_match:
            return {"success": True, "response": self.linkedin(linkedin_match.group(1).strip())}
        return {"success": False, "response": "I did not find a social media command, sir."}

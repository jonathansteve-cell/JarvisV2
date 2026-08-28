"""Safe Roblox assistance for Jarvis V2.

Jarvis helps with LEGITIMATE Roblox activities only:

- opening Roblox and official pages (Robux store, Creator Hub, DevEx info)
- searching for games to play
- timed grind sessions with focus goals
- persistent goals and progress logging (local JSON storage)
- honest guidance on earning Robux safely

Jarvis refuses cheating: exploits, injectors/executors, aimbots, automation bots,
account theft, and fake "free Robux" generators. Those violate the Roblox Terms
of Use and often steal accounts.
"""

from __future__ import annotations

import json
import random
import re
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

LINKS = {
    "discover": "https://www.roblox.com/discover",
    "search": "https://www.roblox.com/search/games?keyword=",
    "robux": "https://www.roblox.com/upgrades/robux",
    "creator_hub": "https://create.roblox.com/",
    "devex": "https://en.help.roblox.com/hc/en-us/articles/203313100",
}

CHEAT_INTENTS = [
    "exploit",
    "exploiter",
    "injector",
    "executor",
    "aimbot",
    "wallhack",
    "fly hack",
    "speed hack",
    "cheat",
    "hack roblox",
    "hack account",
    "steal account",
    "bypass",
    "robux generator",
    "free robux generator",
    "free robux no verification",
    "bot farm",
    "auto farm bot",
    "macro farm",
]

LEGIT_ROBUX_GUIDANCE = (
    "Sir, there is no legitimate Robux generator. Robux can only be earned or bought "
    "safely through official channels: purchasing them on the Roblox website, receiving "
    "the monthly stipend with a Roblox Premium subscription, selling clothing, items, or "
    "game passes you create, or earning from experiences you build and then exchanging "
    "earned Robux for real money through DevEx once you meet the requirements. Anything "
    "promising free generated Robux is a scam that risks your account, sir."
)

GRIND_TIPS = [
    "Set a clear goal before you start, sir. Focused grinding beats aimless play.",
    "Short breaks every twenty-five minutes keep your reactions sharp, sir.",
    "Track what you earn each session so progress stays visible, sir.",
    "Stop and rest when it stops being fun. Games are meant to be enjoyed, sir.",
]


class RobloxController:
    """Grind sessions, goals, progress tracking, and official Roblox links."""

    def __init__(self, config: Any) -> None:
        self.config = config
        data_dir = Path(config.get("paths.data_dir", "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "roblox.json"
        self.data: dict[str, Any] = {"goals": [], "progress": [], "sessions": []}
        self._load()
        self.session: dict[str, Any] | None = None
        self._timer: threading.Timer | None = None

    # ------------------------------------------------------------------ storage
    def _load(self) -> None:
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except Exception:
                pass

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------ helpers
    def _open(self, url: str) -> bool:
        if not self.config.get("roblox.allow_web_open", True):
            return False
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False

    def _minutes_today(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        return sum(int(s.get("minutes", 0)) for s in self.data["sessions"] if s.get("date") == today)

    # ------------------------------------------------------------------ sessions
    def start_session(self, minutes: int, focus: str = "") -> str:
        if self.session:
            return (
                f"A grind session is already running, sir. "
                f"{self.session_status('Tell me to end the grind session when you finish.')}"
            )
        minutes = max(1, min(int(minutes), 600))
        now = datetime.now()
        self.session = {
            "started_at": now.isoformat(timespec="seconds"),
            "minutes": minutes,
            "focus": focus.strip(),
        }
        self._timer = threading.Timer(minutes * 60, self._auto_complete)
        self._timer.daemon = True
        self._timer.start()
        focus_text = f" Focus: {focus.strip()}." if focus.strip() else ""
        tip = random.choice(GRIND_TIPS)
        return (
            f"Grind session started, sir. Timer set for {minutes} minutes.{focus_text} "
            f"I will log it when the time is up. {tip}"
        )

    def _auto_complete(self) -> None:
        if self.session:
            self.end_session(auto=True)

    def end_session(self, auto: bool = False) -> str:
        if not self.session:
            return "No grind session is currently running, sir."
        started = datetime.fromisoformat(self.session["started_at"])
        elapsed = max(1, round((datetime.now() - started).total_seconds() / 60))
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "started_at": self.session["started_at"],
            "minutes": min(elapsed, int(self.session["minutes"]) + 5),
            "focus": self.session.get("focus", ""),
            "auto_completed": auto,
        }
        self.data["sessions"].append(entry)
        self._save()
        focus = self.session.get("focus", "")
        self.session = None
        if self._timer:
            self._timer.cancel()
            self._timer = None
        prefix = "Time is up. " if auto else "Session ended. "
        focus_text = f" Objective: {focus}." if focus else ""
        return (
            f"{prefix}Logged {entry['minutes']} minutes of grinding today.{focus_text} "
            f"That brings today's total to {self._minutes_today()} minutes, sir."
        )

    def session_status(self, suffix: str = "") -> str:
        if not self.session:
            return "No grind session is running, sir." + (" " + suffix if suffix else "")
        started = datetime.fromisoformat(self.session["started_at"])
        remaining = int(self.session["minutes"]) - round((datetime.now() - started).total_seconds() / 60)
        focus = self.session.get("focus", "")
        focus_text = f" Focus: {focus}." if focus else ""
        if remaining > 0:
            return f"Grind session active, sir. About {remaining} minutes remaining.{focus_text}"
        return f"Grind session time is up, sir. Say 'end grind session' to log it.{focus_text}"

    # ------------------------------------------------------------------ goals
    def add_goal(self, text: str) -> str:
        text = text.strip().strip(":").strip()
        if not text:
            return "What goal should I record, sir?"
        self.data["goals"].append({"text": text, "done": False, "created_at": datetime.now().isoformat(timespec="seconds")})
        self._save()
        return f"Roblox goal recorded, sir: {text}. Say 'show Roblox goals' to review them."

    def list_goals(self) -> str:
        goals = self.data["goals"]
        if not goals:
            return "You have no Roblox goals yet, sir. Say 'set Roblox goal' followed by your objective."
        lines = [
            f"{'[DONE] ' if goal['done'] else ''}{index}. {goal['text']}"
            for index, goal in enumerate(goals, start=1)
        ]
        done = sum(1 for goal in goals if goal["done"])
        return f"You have {done} of {len(goals)} Roblox goals completed, sir: " + "; ".join(lines) + "."

    def complete_goal(self, query: str) -> str:
        query = query.strip().lower()
        for goal in self.data["goals"]:
            if not goal["done"] and (query in goal["text"].lower() or goal["text"].lower() in query):
                goal["done"] = True
                self._save()
                return f"Marking goal complete, sir: {goal['text']}. Well done."
        if query.isdigit() and 1 <= int(query) <= len(self.data["goals"]):
            goal = self.data["goals"][int(query) - 1]
            goal["done"] = True
            self._save()
            return f"Marking goal complete, sir: {goal['text']}. Well done."
        return "I could not find that goal, sir. Say 'show Roblox goals' to list them."

    def log_progress(self, text: str) -> str:
        text = text.strip().strip(":").strip()
        if not text:
            return "What progress should I log, sir?"
        self.data["progress"].append({"text": text, "created_at": datetime.now().isoformat(timespec="seconds")})
        self._save()
        return f"Progress logged, sir: {text}."

    def stats(self) -> str:
        sessions = self.data["sessions"]
        total_minutes = sum(int(s.get("minutes", 0)) for s in sessions)
        goals = self.data["goals"]
        done = sum(1 for goal in goals if goal["done"])
        active = "Session active now, sir." if self.session else "No session running."
        recent = self.data["progress"][-3:]
        recent_text = ""
        if recent:
            recent_text = " Recent progress: " + "; ".join(item["text"] for item in recent) + "."
        return (
            f"Roblox stats, sir: {len(sessions)} grind sessions logged for {total_minutes} total minutes, "
            f"{self._minutes_today()} minutes today, {done} of {len(goals)} goals complete. {active}{recent_text}"
        )

    # ------------------------------------------------------------------ guidance
    def robux_guidance(self) -> str:
        return LEGIT_ROBUX_GUIDANCE

    def safety_note(self) -> str:
        return (
            "I cannot help with exploits, executors, aimbots, farming bots, or Robux generators, sir. "
            "They break the Roblox Terms of Use and usually steal accounts. " + LEGIT_ROBUX_GUIDANCE
        )

    def capability_summary(self) -> str:
        return (
            "On the Roblox front, sir, I can open Roblox and its official pages, search for games, "
            "run timed grind sessions, track goals and progress, and explain how to earn Robux safely. "
            "I will not touch cheats or generators."
        )

    # ------------------------------------------------------------------ router
    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower().strip()
        if not any(term in lower for term in ["roblox", "robux", "grind", "devex"]):
            return {"success": False, "response": "I did not find a Roblox command, sir."}

        if any(term in lower for term in CHEAT_INTENTS):
            return {"success": True, "response": self.safety_note(), "data": {"refused": True}}

        # Official links ---------------------------------------------------
        if re.search(r"(open|go to|launch).*(creator hub|creator dashboard)", lower):
            opened = self._open(LINKS["creator_hub"])
            return {"success": True, "response": "Opening the Roblox Creator Hub, sir." if opened else "Web opening is disabled, but the Creator Hub is at create.roblox.com, sir."}
        if "devex" in lower:
            opened = self._open(LINKS["devex"])
            return {"success": True, "response": "Opening the official DevEx information page, sir." if opened else "DevEx details are on the Roblox support site, article 203313100, sir."}
        if re.search(r"(open|go to).*(robux|roblox store)", lower) and "how" not in lower:
            opened = self._open(LINKS["robux"])
            return {"success": True, "response": "Opening the official Robux page, sir." if opened else "The official Robux page is at roblox.com/upgrades/robux, sir."}
        if re.search(r"^(open|launch) roblox$|open roblox\b", lower) and "search" not in lower and "studio" not in lower:
            opened = self._open(LINKS["discover"])
            return {"success": True, "response": "Opening Roblox, sir." if opened else "Web opening is disabled, but Roblox is at roblox.com, sir."}

        # Game search --------------------------------------------------------
        search_match = re.search(r"(?:search|find)(?: roblox)?(?: game[s]?| for)?(?: for)? (.+)", lower)
        if search_match and ("roblox" in lower or "game" in lower):
            query = search_match.group(1).strip()
            query = re.sub(r"^(games?|on roblox)\s*", "", query).strip()
            if query:
                opened = self._open(LINKS["search"] + query.replace(" ", "+"))
                return {"success": True, "response": f"Searching Roblox for {query}, sir."}

        # Grind sessions -------------------------------------------------------
        if "grind" in lower:
            if any(word in lower for word in ["end", "stop", "finish"]):
                return {"success": True, "response": self.end_session("time" in lower or "up" in lower)}
            if "status" in lower or "how long" in lower or "remaining" in lower:
                return {"success": True, "response": self.session_status()}
            session_match = re.search(r"(?:start|begin)(?: a)?(?: (\d+)[ -]?(?:minute|min|hour|hr)[s]?)?(?: roblox)? grind(?: session)?(?: for (.+))?", lower)
            if session_match:
                minutes = 30
                if session_match.group(1):
                    minutes = int(session_match.group(1))
                    if "hour" in session_match.group(0) and minutes <= 24:
                        minutes *= 60
                focus = session_match.group(2) or ""
                return {"success": True, "response": self.start_session(minutes, focus)}
            return {"success": True, "response": "Tell me, for example: start a 30 minute Roblox grind session for daily quests, sir."}

        # Robux guidance -----------------------------------------------------
        if "robux" in lower:
            if re.search(r"(how|way|ways|earn|get|safe|legit|free)", lower):
                return {"success": True, "response": self.robux_guidance()}
            return {"success": True, "response": self.robux_guidance()}

        # Goals and progress ---------------------------------------------------
        if re.search(r"(?:show|list|what are).*(goal)", lower) or lower.strip() in {"roblox goals", "goals"}:
            return {"success": True, "response": self.list_goals()}
        complete_match = re.search(r"(?:complete|completed|finish|finished|done with)(?: roblox)? goal(?: number)? ?(\d+|.*)", lower)
        if complete_match:
            return {"success": True, "response": self.complete_goal(complete_match.group(1))}
        progress_match = re.search(r"(?:log|record)(?: roblox)? progress[: ]+(.+)", lower)
        if progress_match:
            return {"success": True, "response": self.log_progress(progress_match.group(1))}
        goal_match = re.search(r"(?:set|add|new) (?:a |new )?(?:roblox )?goal[: ]+(.+)", lower)
        if goal_match:
            return {"success": True, "response": self.add_goal(goal_match.group(1))}

        # Stats and help ---------------------------------------------------------
        if "stat" in lower or "progress" in lower:
            return {"success": True, "response": self.stats(), "data": dict(self.data)}
        if "help" in lower or "what can you" in lower:
            return {"success": True, "response": self.capability_summary()}

        return {"success": False, "response": "I did not find a Roblox command, sir."}

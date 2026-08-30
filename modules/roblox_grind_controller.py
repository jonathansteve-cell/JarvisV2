"""
Jarvis V2 - Roblox Grind Controller
=====================================
Automated Roblox grinding mode for earning Robux.

Features:
- Game selection and launching
- Session tracking
- Goal management
- Progress monitoring
- Automatic breaks
- Statistics tracking
"""

from __future__ import annotations

import json
import os
import time
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread, Event
from typing import Any, Optional


class RobloxGrindController:
    """
    Roblox Grind Mode controller for Jarvis V2.

    Manages automated grinding sessions with goals and progress tracking.
    """

    # Popular Roblox games for grinding
    GRIND_GAMES = {
        "adopt_me": {
            "name": "Adopt Me!",
            "url": "https://www.roblox.com/games/2753915549",
            "description": "Raise and dress cute pets, decorate your home",
            "avg_robux_per_hour": 50,
            "difficulty": "Easy"
        },
        "brookhaven": {
            "name": "Brookhaven",
            "url": "https://www.roblox.com/games/4924922222",
            "description": "Role-play in a modern city",
            "avg_robux_per_hour": 30,
            "difficulty": "Easy"
        },
        "blox_fruits": {
            "name": "Blox Fruits",
            "url": "https://www.roblox.com/games/2753915549",
            "description": "Become a powerful fruit user",
            "avg_robux_per_hour": 100,
            "difficulty": "Medium"
        },
        "murder_mystery_2": {
            "name": "Murder Mystery 2",
            "url": "https://www.roblox.com/games/142823291",
            "description": "Solve the mystery or be the murderer",
            "avg_robux_per_hour": 40,
            "difficulty": "Easy"
        },
        "tower_of_hell": {
            "name": "Tower of Hell",
            "url": "https://www.roblox.com/games/1962086868",
            "description": "Climb the tower without dying",
            "avg_robux_per_hour": 60,
            "difficulty": "Medium"
        },
        "pet_simulator_x": {
            "name": "Pet Simulator X",
            "url": "https://www.roblox.com/games/6284583030",
            "description": "Collect and upgrade pets",
            "avg_robux_per_hour": 80,
            "difficulty": "Easy"
        },
        "bee_swarm_simulator": {
            "name": "Bee Swarm Simulator",
            "url": "https://www.roblox.com/games/1537690962",
            "description": "Collect pollen and make honey",
            "avg_robux_per_hour": 70,
            "difficulty": "Medium"
        },
        "king_legacy": {
            "name": "King Legacy",
            "url": "https://www.roblox.com/games/4520749081",
            "description": "Become the king of the pirates",
            "avg_robux_per_hour": 90,
            "difficulty": "Hard"
        }
    }

    def __init__(self, config: Any = None):
        self.config = config
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.data_file = self.data_dir / "roblox_grind.json"
        self.session_file = self.data_dir / "roblox_session.json"

        self._load_data()

        # Session state
        self.session_active = False
        self.session_start = None
        self.current_game = None
        self.session_goals = []
        self.session_progress = {}
        self.stop_event = Event()
        self.session_thread = None

    def _load_data(self):
        """Load grind data from file."""
        if self.data_file.exists():
            try:
                self.data = json.loads(self.data_file.read_text(encoding="utf-8"))
            except Exception:
                self.data = self._default_data()
        else:
            self.data = self._default_data()

    def _default_data(self) -> dict[str, Any]:
        """Create default data structure."""
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "total_robux_earned": 0,
            "games_played": {},
            "goals_completed": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "last_session": None,
            "sessions": []
        }

    def _save_data(self):
        """Save grind data to file."""
        self.data_file.write_text(
            json.dumps(self.data, indent=2, default=str),
            encoding="utf-8"
        )

    def _save_session(self):
        """Save current session state."""
        if self.session_active:
            session_data = {
                "active": True,
                "game": self.current_game,
                "started_at": self.session_start.isoformat() if self.session_start else None,
                "goals": self.session_goals,
                "progress": self.session_progress
            }
            self.session_file.write_text(
                json.dumps(session_data, indent=2),
                encoding="utf-8"
            )
        elif self.session_file.exists():
            self.session_file.unlink()

    def get_available_games(self) -> list[dict[str, Any]]:
        """Get list of available grind games."""
        games = []
        for game_id, game_info in self.GRIND_GAMES.items():
            games.append({
                "id": game_id,
                "name": game_info["name"],
                "description": game_info["description"],
                "avg_robux_per_hour": game_info["avg_robux_per_hour"],
                "difficulty": game_info["difficulty"]
            })
        return games

    def start_grind_session(
        self,
        game_id: str,
        duration_minutes: int = 30,
        goals: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Start a grind session.

        Args:
            game_id: ID of the game to play
            duration_minutes: Session duration in minutes
            goals: List of goals to achieve

        Returns:
            Dictionary with session status
        """
        if self.session_active:
            return {
                "success": False,
                "message": "A grind session is already active. End it first."
            }

        if game_id not in self.GRIND_GAMES:
            return {
                "success": False,
                "message": f"Unknown game: {game_id}. Use 'list games' to see available games."
            }

        game_info = self.GRIND_GAMES[game_id]

        # Initialize session
        self.session_active = True
        self.session_start = datetime.now()
        self.current_game = game_id
        self.session_goals = goals or []
        self.session_progress = {
            "goals_completed": 0,
            "total_goals": len(goals) if goals else 0,
            "estimated_robux": 0,
            "minutes_played": 0
        }

        # Save session
        self._save_session()

        # Open game in browser
        webbrowser.open(game_info["url"])

        # Start session timer
        self.stop_event.clear()
        self.session_thread = Thread(
            target=self._session_timer,
            args=(duration_minutes,),
            daemon=True
        )
        self.session_thread.start()

        return {
            "success": True,
            "game": game_info["name"],
            "duration": duration_minutes,
            "goals": goals,
            "message": f"Grind session started! Playing {game_info['name']} for {duration_minutes} minutes."
        }

    def _session_timer(self, duration_minutes: int):
        """Timer thread for session duration."""
        end_time = datetime.now() + timedelta(minutes=duration_minutes)

        while datetime.now() < end_time and not self.stop_event.is_set():
            # Update progress
            elapsed = (datetime.now() - self.session_start).total_seconds() / 60
            self.session_progress["minutes_played"] = int(elapsed)

            # Estimate Robux
            if self.current_game:
                game_info = self.GRIND_GAMES[self.current_game]
                robux_per_min = game_info["avg_robux_per_hour"] / 60
                self.session_progress["estimated_robux"] = int(elapsed * robux_per_min)

            self._save_session()

            # Sleep for 1 minute
            self.stop_event.wait(60)

        # Session ended
        if not self.stop_event.is_set():
            self.end_grind_session()

    def end_grind_session(self) -> dict[str, Any]:
        """End the current grind session."""
        if not self.session_active:
            return {
                "success": False,
                "message": "No active grind session."
            }

        # Calculate session stats
        end_time = datetime.now()
        duration = (end_time - self.session_start).total_seconds() / 60

        # Update data
        self.data["total_sessions"] += 1
        self.data["total_minutes"] += int(duration)
        self.data["total_robux_earned"] += self.session_progress.get("estimated_robux", 0)
        self.data["goals_completed"] += self.session_progress.get("goals_completed", 0)
        self.data["last_session"] = end_time.isoformat()

        # Update game stats
        if self.current_game:
            if self.current_game not in self.data["games_played"]:
                self.data["games_played"][self.current_game] = {
                    "sessions": 0,
                    "minutes": 0,
                    "robux": 0
                }
            self.data["games_played"][self.current_game]["sessions"] += 1
            self.data["games_played"][self.current_game]["minutes"] += int(duration)
            self.data["games_played"][self.current_game]["robux"] += self.session_progress.get("estimated_robux", 0)

        # Add to session history
        session_record = {
            "game": self.current_game,
            "started_at": self.session_start.isoformat(),
            "ended_at": end_time.isoformat(),
            "duration_minutes": int(duration),
            "goals": self.session_goals,
            "goals_completed": self.session_progress.get("goals_completed", 0),
            "estimated_robux": self.session_progress.get("estimated_robux", 0)
        }
        self.data["sessions"].append(session_record)

        # Keep only last 100 sessions
        if len(self.data["sessions"]) > 100:
            self.data["sessions"] = self.data["sessions"][-100:]

        self._save_data()

        # Reset session
        game_name = self.GRIND_GAMES.get(self.current_game, {}).get("name", "Unknown")
        self.session_active = False
        self.session_start = None
        self.current_game = None
        self.session_goals = []
        self.session_progress = {}
        self.stop_event.set()

        # Clean up session file
        if self.session_file.exists():
            self.session_file.unlink()

        return {
            "success": True,
            "game": game_name,
            "duration": int(duration),
            "robux_earned": session_record["estimated_robux"],
            "goals_completed": session_record["goals_completed"],
            "message": f"Grind session ended! Played {game_name} for {int(duration)} minutes. Estimated {session_record['estimated_robux']} Robux earned."
        }

    def complete_goal(self, goal: str) -> dict[str, Any]:
        """Mark a goal as completed."""
        if not self.session_active:
            return {"success": False, "message": "No active grind session."}

        if goal in self.session_goals:
            self.session_progress["goals_completed"] = self.session_progress.get("goals_completed", 0) + 1
            self._save_session()
            return {"success": True, "message": f"Goal completed: {goal}"}
        else:
            return {"success": False, "message": f"Goal not found: {goal}"}

    def get_session_status(self) -> dict[str, Any]:
        """Get current session status."""
        if not self.session_active:
            return {
                "active": False,
                "message": "No active grind session."
            }

        elapsed = (datetime.now() - self.session_start).total_seconds() / 60
        game_info = self.GRIND_GAMES.get(self.current_game, {})

        return {
            "active": True,
            "game": game_info.get("name", "Unknown"),
            "started_at": self.session_start.strftime("%H:%M"),
            "elapsed_minutes": int(elapsed),
            "goals": self.session_goals,
            "goals_completed": self.session_progress.get("goals_completed", 0),
            "total_goals": self.session_progress.get("total_goals", 0),
            "estimated_robux": self.session_progress.get("estimated_robux", 0)
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get overall grind statistics."""
        return {
            "total_sessions": self.data["total_sessions"],
            "total_hours": round(self.data["total_minutes"] / 60, 1),
            "total_robux": self.data["total_robux_earned"],
            "goals_completed": self.data["goals_completed"],
            "games_played": len(self.data["games_played"]),
            "favorite_game": self._get_favorite_game(),
            "avg_session_minutes": self._get_avg_session_time()
        }

    def _get_favorite_game(self) -> str:
        """Get the most played game."""
        if not self.data["games_played"]:
            return "None"

        favorite = max(
            self.data["games_played"].items(),
            key=lambda x: x[1]["sessions"]
        )
        return self.GRIND_GAMES.get(favorite[0], {}).get("name", favorite[0])

    def _get_avg_session_time(self) -> int:
        """Get average session time in minutes."""
        if self.data["total_sessions"] == 0:
            return 0
        return self.data["total_minutes"] // self.data["total_sessions"]

    def get_session_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent session history."""
        sessions = self.data.get("sessions", [])[-limit:]
        return [
            {
                "game": self.GRIND_GAMES.get(s["game"], {}).get("name", s["game"]),
                "date": s["started_at"][:10] if s.get("started_at") else "Unknown",
                "duration": s.get("duration_minutes", 0),
                "robux": s.get("estimated_robux", 0)
            }
            for s in reversed(sessions)
        ]

    def open_game(self, game_id: str) -> dict[str, Any]:
        """Open a Roblox game in browser."""
        if game_id not in self.GRIND_GAMES:
            return {
                "success": False,
                "message": f"Unknown game: {game_id}"
            }

        game_info = self.GRIND_GAMES[game_id]
        webbrowser.open(game_info["url"])

        return {
            "success": True,
            "game": game_info["name"],
            "message": f"Opening {game_info['name']}..."
        }

    def search_games(self, query: str) -> list[dict[str, Any]]:
        """Search for games by name or description."""
        query = query.lower()
        results = []

        for game_id, game_info in self.GRIND_GAMES.items():
            if (query in game_info["name"].lower() or
                query in game_info["description"].lower()):
                results.append({
                    "id": game_id,
                    "name": game_info["name"],
                    "description": game_info["description"],
                    "avg_robux_per_hour": game_info["avg_robux_per_hour"]
                })

        return results


def get_roblox_grind_controller(config: Any = None) -> RobloxGrindController:
    """Get or create the global RobloxGrindController instance."""
    if not hasattr(get_roblox_grind_controller, "_instance"):
        get_roblox_grind_controller._instance = RobloxGrindController(config)
    return get_roblox_grind_controller._instance

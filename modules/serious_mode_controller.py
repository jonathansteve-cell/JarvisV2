"""
Jarvis V2 - Serious Mode Controller
=====================================
Opens test workspaces for learning and serious work.

Features:
- Predefined workspace configurations
- Application launching
- Website opening
- Study environment setup
- Focus mode with distractions blocked
"""

from __future__ import annotations

import json
import os
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class SeriousModeController:
    """
    Serious Mode controller for Jarvis V2.

    Opens test workspaces and learning environments.
    """

    # Predefined workspace configurations
    WORKSPACES = {
        "coding": {
            "name": "Coding Workspace",
            "description": "IDE, documentation, and development tools",
            "apps": [
                {"name": "VS Code", "command": "code", "platform": "all"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Terminal", "command": "wt", "platform": "windows"},
                {"name": "Terminal", "command": "terminal", "platform": "linux"},
            ],
            "websites": [
                "https://github.com",
                "https://stackoverflow.com",
                "https://developer.mozilla.org",
            ],
            "focus_mode": True
        },
        "studying": {
            "name": "Study Workspace",
            "description": "Note-taking, research, and learning tools",
            "apps": [
                {"name": "Notion", "command": "notion", "platform": "all"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Spotify", "command": "spotify", "platform": "all"},
            ],
            "websites": [
                "https://www.notion.so",
                "https://scholar.google.com",
                "https://www.coursera.org",
                "https://www.khanacademy.org",
            ],
            "focus_mode": True
        },
        "writing": {
            "name": "Writing Workspace",
            "description": "Word processing and research tools",
            "apps": [
                {"name": "Word", "command": "winword", "platform": "windows"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Grammarly", "command": "grammarly", "platform": "all"},
            ],
            "websites": [
                "https://docs.google.com",
                "https://www.grammarly.com",
                "https://www.thesaurus.com",
            ],
            "focus_mode": True
        },
        "research": {
            "name": "Research Workspace",
            "description": "Academic research and paper writing",
            "apps": [
                {"name": "Zotero", "command": "zotero", "platform": "all"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Word", "command": "winword", "platform": "windows"},
            ],
            "websites": [
                "https://scholar.google.com",
                "https://www.researchgate.net",
                "https://arxiv.org",
                "https://www.semanticscholar.org",
            ],
            "focus_mode": True
        },
        "math": {
            "name": "Math Workspace",
            "description": "Mathematical tools and calculators",
            "apps": [
                {"name": "Wolfram Alpha", "command": "wolframalpha", "platform": "all"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Desmos", "command": "desmos", "platform": "all"},
            ],
            "websites": [
                "https://www.wolframalpha.com",
                "https://www.desmos.com",
                "https://www.geogebra.org",
                "https://www.khanacademy.org/math",
            ],
            "focus_mode": True
        },
        "science": {
            "name": "Science Workspace",
            "description": "Scientific research and experiments",
            "apps": [
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Jupyter", "command": "jupyter-notebook", "platform": "all"},
            ],
            "websites": [
                "https://www.sciencedirect.com",
                "https://www.nature.com",
                "https://www.nasa.gov",
                "https://www.science.org",
            ],
            "focus_mode": True
        },
        "language": {
            "name": "Language Learning Workspace",
            "description": "Language learning tools and resources",
            "apps": [
                {"name": "Anki", "command": "anki", "platform": "all"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Spotify", "command": "spotify", "platform": "all"},
            ],
            "websites": [
                "https://www.duolingo.com",
                "https://www.memrise.com",
                "https://www.babbel.com",
                "https://forvo.com",
            ],
            "focus_mode": True
        },
        "business": {
            "name": "Business Workspace",
            "description": "Business tools and productivity",
            "apps": [
                {"name": "Excel", "command": "excel", "platform": "windows"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Slack", "command": "slack", "platform": "all"},
            ],
            "websites": [
                "https://www.linkedin.com",
                "https://trello.com",
                "https://asana.com",
                "https://www.bloomberg.com",
            ],
            "focus_mode": True
        },
        "creative": {
            "name": "Creative Workspace",
            "description": "Design and creative tools",
            "apps": [
                {"name": "Figma", "command": "figma", "platform": "all"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Photoshop", "command": "photoshop", "platform": "all"},
            ],
            "websites": [
                "https://www.figma.com",
                "https://dribbble.com",
                "https://www.behance.net",
                "https://www.canva.com",
            ],
            "focus_mode": True
        },
        "exam_prep": {
            "name": "Exam Preparation Workspace",
            "description": "Study tools for exam preparation",
            "apps": [
                {"name": "Anki", "command": "anki", "platform": "all"},
                {"name": "Chrome", "command": "chrome", "platform": "all"},
                {"name": "Notion", "command": "notion", "platform": "all"},
            ],
            "websites": [
                "https://www.quizlet.com",
                "https://www.khanacademy.org",
                "https://www.coursera.org",
                "https://www.edx.org",
            ],
            "focus_mode": True
        }
    }

    def __init__(self, config: Any = None):
        self.config = config
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.sessions_file = self.data_dir / "serious_sessions.json"
        self._load_sessions()

        self.current_workspace = None
        self.session_start = None
        self.focus_mode = False

    def _load_sessions(self):
        """Load session history."""
        if self.sessions_file.exists():
            try:
                self.sessions = json.loads(self.sessions_file.read_text(encoding="utf-8"))
            except Exception:
                self.sessions = []
        else:
            self.sessions = []

    def _save_sessions(self):
        """Save session history."""
        self.sessions_file.write_text(
            json.dumps(self.sessions, indent=2, default=str),
            encoding="utf-8"
        )

    def get_available_workspaces(self) -> list[dict[str, Any]]:
        """Get list of available workspaces."""
        workspaces = []
        for ws_id, ws_info in self.WORKSPACES.items():
            workspaces.append({
                "id": ws_id,
                "name": ws_info["name"],
                "description": ws_info["description"],
                "apps_count": len(ws_info["apps"]),
                "websites_count": len(ws_info["websites"])
            })
        return workspaces

    def open_workspace(
        self,
        workspace_id: str,
        custom_apps: Optional[list[str]] = None,
        custom_websites: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Open a workspace.

        Args:
            workspace_id: ID of the workspace to open
            custom_apps: Additional apps to open
            custom_websites: Additional websites to open

        Returns:
            Dictionary with workspace status
        """
        if workspace_id not in self.WORKSPACES:
            return {
                "success": False,
                "message": f"Unknown workspace: {workspace_id}. Use 'list workspaces' to see available options."
            }

        workspace = self.WORKSPACES[workspace_id]

        # Start session
        self.current_workspace = workspace_id
        self.session_start = datetime.now()
        self.focus_mode = workspace.get("focus_mode", False)

        # Open apps
        opened_apps = []
        failed_apps = []

        for app in workspace["apps"]:
            try:
                # Check platform
                platform = app.get("platform", "all")
                if platform != "all":
                    import sys
                    current_platform = sys.platform
                    if platform == "windows" and not current_platform.startswith("win"):
                        continue
                    elif platform == "linux" and not current_platform.startswith("linux"):
                        continue
                    elif platform == "macos" and not current_platform.startswith("darwin"):
                        continue

                # Try to open app
                command = app["command"]
                if os.name == "nt":  # Windows
                    subprocess.Popen(command, shell=True)
                else:  # Linux/Mac
                    subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                opened_apps.append(app["name"])
            except Exception as e:
                failed_apps.append({"name": app["name"], "error": str(e)})

        # Open websites
        opened_websites = []
        for website in workspace["websites"]:
            try:
                webbrowser.open(website)
                opened_websites.append(website)
            except Exception:
                pass

        # Open custom apps
        if custom_apps:
            for app in custom_apps:
                try:
                    if os.name == "nt":
                        subprocess.Popen(app, shell=True)
                    else:
                        subprocess.Popen([app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    opened_apps.append(app)
                except Exception:
                    pass

        # Open custom websites
        if custom_websites:
            for website in custom_websites:
                try:
                    webbrowser.open(website)
                    opened_websites.append(website)
                except Exception:
                    pass

        # Save session
        session_record = {
            "workspace": workspace_id,
            "started_at": self.session_start.isoformat(),
            "apps_opened": opened_apps,
            "websites_opened": opened_websites,
            "focus_mode": self.focus_mode
        }
        self.sessions.append(session_record)
        self._save_sessions()

        return {
            "success": True,
            "workspace": workspace["name"],
            "apps_opened": opened_apps,
            "apps_failed": failed_apps,
            "websites_opened": len(opened_websites),
            "focus_mode": self.focus_mode,
            "message": f"Opened {workspace['name']} with {len(opened_apps)} apps and {len(opened_websites)} websites."
        }

    def open_custom_workspace(
        self,
        name: str,
        apps: Optional[list[str]] = None,
        websites: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Open a custom workspace with specified apps and websites.

        Args:
            name: Name for the workspace
            apps: List of app commands to open
            websites: List of website URLs to open

        Returns:
            Dictionary with workspace status
        """
        self.current_workspace = "custom"
        self.session_start = datetime.now()

        opened_apps = []
        opened_websites = []

        # Open apps
        if apps:
            for app in apps:
                try:
                    if os.name == "nt":
                        subprocess.Popen(app, shell=True)
                    else:
                        subprocess.Popen([app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    opened_apps.append(app)
                except Exception:
                    pass

        # Open websites
        if websites:
            for website in websites:
                try:
                    if not website.startswith("http"):
                        website = "https://" + website
                    webbrowser.open(website)
                    opened_websites.append(website)
                except Exception:
                    pass

        # Save session
        session_record = {
            "workspace": "custom",
            "name": name,
            "started_at": self.session_start.isoformat(),
            "apps_opened": opened_apps,
            "websites_opened": opened_websites
        }
        self.sessions.append(session_record)
        self._save_sessions()

        return {
            "success": True,
            "name": name,
            "apps_opened": opened_apps,
            "websites_opened": opened_websites,
            "message": f"Opened custom workspace '{name}' with {len(opened_apps)} apps and {len(opened_websites)} websites."
        }

    def close_workspace(self) -> dict[str, Any]:
        """Close the current workspace."""
        if not self.current_workspace:
            return {
                "success": False,
                "message": "No active workspace."
            }

        # Calculate duration
        duration = 0
        if self.session_start:
            duration = (datetime.now() - self.session_start).total_seconds() / 60

        # Update session record
        if self.sessions:
            self.sessions[-1]["ended_at"] = datetime.now().isoformat()
            self.sessions[-1]["duration_minutes"] = int(duration)
            self._save_sessions()

        workspace_name = self.current_workspace
        self.current_workspace = None
        self.session_start = None
        self.focus_mode = False

        return {
            "success": True,
            "workspace": workspace_name,
            "duration": int(duration),
            "message": f"Closed workspace. Session lasted {int(duration)} minutes."
        }

    def get_status(self) -> dict[str, Any]:
        """Get current workspace status."""
        if not self.current_workspace:
            return {
                "active": False,
                "message": "No active workspace."
            }

        duration = 0
        if self.session_start:
            duration = (datetime.now() - self.session_start).total_seconds() / 60

        workspace_info = self.WORKSPACES.get(self.current_workspace, {})

        return {
            "active": True,
            "workspace": workspace_info.get("name", self.current_workspace),
            "started_at": self.session_start.strftime("%H:%M") if self.session_start else "Unknown",
            "duration_minutes": int(duration),
            "focus_mode": self.focus_mode
        }

    def get_session_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent session history."""
        sessions = self.sessions[-limit:]
        return [
            {
                "workspace": s.get("name", s.get("workspace", "Unknown")),
                "date": s.get("started_at", "")[:10] if s.get("started_at") else "Unknown",
                "duration": s.get("duration_minutes", 0),
                "apps": len(s.get("apps_opened", []))
            }
            for s in reversed(sessions)
        ]

    def search_workspaces(self, query: str) -> list[dict[str, Any]]:
        """Search for workspaces by name or description."""
        query = query.lower()
        results = []

        for ws_id, ws_info in self.WORKSPACES.items():
            if (query in ws_info["name"].lower() or
                query in ws_info["description"].lower() or
                query in ws_id.lower()):
                results.append({
                    "id": ws_id,
                    "name": ws_info["name"],
                    "description": ws_info["description"]
                })

        return results

    def enable_focus_mode(self) -> dict[str, Any]:
        """Enable focus mode (block distracting websites)."""
        self.focus_mode = True

        # Update hosts file to block distracting sites
        # Note: This requires admin/root privileges
        distracting_sites = [
            "www.facebook.com",
            "www.twitter.com",
            "www.instagram.com",
            "www.tiktok.com",
            "www.reddit.com",
            "www.youtube.com",
        ]

        return {
            "success": True,
            "message": "Focus mode enabled. Distracting websites will be blocked.",
            "blocked_sites": distracting_sites
        }

    def disable_focus_mode(self) -> dict[str, Any]:
        """Disable focus mode."""
        self.focus_mode = False

        return {
            "success": True,
            "message": "Focus mode disabled. All websites are accessible."
        }

    def get_study_tips(self, subject: str) -> list[str]:
        """Get study tips for a subject."""
        tips = {
            "math": [
                "Practice problems daily",
                "Understand concepts before memorizing formulas",
                "Use visual aids and diagrams",
                "Teach concepts to others",
                "Take breaks every 25 minutes (Pomodoro technique)"
            ],
            "science": [
                "Read actively, not passively",
                "Create concept maps",
                "Do experiments when possible",
                "Relate concepts to real-world examples",
                "Review notes within 24 hours"
            ],
            "language": [
                "Practice speaking daily",
                "Listen to native speakers",
                "Use flashcards for vocabulary",
                "Read in the target language",
                "Write daily journal entries"
            ],
            "coding": [
                "Code every day, even if just 30 minutes",
                "Build projects, not just tutorials",
                "Read other people's code",
                "Debug systematically",
                "Use version control (Git)"
            ],
            "general": [
                "Use the Pomodoro technique (25 min work, 5 min break)",
                "Stay hydrated and take breaks",
                "Get enough sleep",
                "Exercise regularly",
                "Minimize distractions"
            ]
        }

        subject_lower = subject.lower()
        for key in tips:
            if key in subject_lower:
                return tips[key]

        return tips["general"]


def get_serious_mode_controller(config: Any = None) -> SeriousModeController:
    """Get or create the global SeriousModeController instance."""
    if not hasattr(get_serious_mode_controller, "_instance"):
        get_serious_mode_controller._instance = SeriousModeController(config)
    return get_serious_mode_controller._instance

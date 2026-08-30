"""
Jarvis V2 - User Management System
====================================
Handles user registration, profiles, and preferences.

Features:
- User sign-up and registration
- Profile management
- Preferences storage
- First-run detection
- Secure password handling
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class UserManager:
    """
    Manages user accounts and profiles for Jarvis V2.

    Features:
    - User registration and sign-up
    - Profile management
    - Preferences storage
    - First-run detection
    - Secure credential storage
    """

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.users_file = data_dir / "users.json"
        self.current_user_file = data_dir / "current_user.json"
        self.preferences_file = data_dir / "user_preferences.json"

        self._users: dict[str, dict[str, Any]] = {}
        self._current_user: Optional[dict[str, Any]] = None
        self._preferences: dict[str, Any] = {}

        self._load_users()
        self._load_current_user()
        self._load_preferences()

    def _load_users(self):
        """Load users from file."""
        if self.users_file.exists():
            try:
                self._users = json.loads(self.users_file.read_text(encoding="utf-8"))
            except Exception:
                self._users = {}

    def _save_users(self):
        """Save users to file."""
        self.users_file.write_text(
            json.dumps(self._users, indent=2, default=str),
            encoding="utf-8"
        )

    def _load_current_user(self):
        """Load current user session."""
        if self.current_user_file.exists():
            try:
                self._current_user = json.loads(
                    self.current_user_file.read_text(encoding="utf-8")
                )
            except Exception:
                self._current_user = None

    def _save_current_user(self):
        """Save current user session."""
        if self._current_user:
            self.current_user_file.write_text(
                json.dumps(self._current_user, indent=2, default=str),
                encoding="utf-8"
            )
        elif self.current_user_file.exists():
            self.current_user_file.unlink()

    def _load_preferences(self):
        """Load user preferences."""
        if self.preferences_file.exists():
            try:
                self._preferences = json.loads(
                    self.preferences_file.read_text(encoding="utf-8")
                )
            except Exception:
                self._preferences = {}

    def _save_preferences(self):
        """Save user preferences."""
        self.preferences_file.write_text(
            json.dumps(self._preferences, indent=2),
            encoding="utf-8"
        )

    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA-256
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100000,
        )
        return key.hex(), salt

    def _verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify a password against its hash."""
        key, _ = self._hash_password(password, salt)
        return secrets.compare_digest(key, hashed)

    def is_first_run(self) -> bool:
        """Check if this is the first time running Jarvis."""
        return len(self._users) == 0

    def has_users(self) -> bool:
        """Check if any users are registered."""
        return len(self._users) > 0

    def register_user(
        self,
        username: str,
        password: str,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Register a new user.

        Args:
            username: Unique username
            password: User password
            display_name: Display name (optional)
            email: Email address (optional)

        Returns:
            Tuple of (success, message)
        """
        # Validate username
        username = username.strip().lower()
        if not username:
            return False, "Username cannot be empty"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 30:
            return False, "Username must be 30 characters or less"
        if not all(c.isalnum() or c in "._-" for c in username):
            return False, "Username can only contain letters, numbers, dots, hyphens, and underscores"
        if username in self._users:
            return False, "Username already exists"

        # Validate password
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if len(password) > 128:
            return False, "Password must be 128 characters or less"

        # Hash password
        hashed, salt = self._hash_password(password)

        # Create user
        user = {
            "username": username,
            "display_name": display_name or username,
            "email": email,
            "password_hash": hashed,
            "password_salt": salt,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "login_count": 0,
            "preferences": {},
        }

        self._users[username] = user
        self._save_users()

        return True, "User registered successfully"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Login a user.

        Args:
            username: Username
            password: Password

        Returns:
            Tuple of (success, message)
        """
        username = username.strip().lower()

        if username not in self._users:
            return False, "Invalid username or password"

        user = self._users[username]

        if not self._verify_password(password, user["password_hash"], user["password_salt"]):
            return False, "Invalid username or password"

        # Update login info
        user["last_login"] = datetime.now().isoformat()
        user["login_count"] = user.get("login_count", 0) + 1
        self._save_users()

        # Set as current user
        self._current_user = {
            "username": username,
            "display_name": user["display_name"],
            "email": user.get("email"),
            "logged_in_at": datetime.now().isoformat(),
        }
        self._save_current_user()

        # Load user preferences
        self._preferences = user.get("preferences", {})
        self._save_preferences()

        return True, "Login successful"

    def logout(self):
        """Logout current user."""
        self._current_user = None
        self._save_current_user()

    def get_current_user(self) -> Optional[dict[str, Any]]:
        """Get the current logged-in user."""
        return self._current_user

    def is_logged_in(self) -> bool:
        """Check if a user is logged in."""
        return self._current_user is not None

    def update_profile(
        self,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> tuple[bool, str]:
        """Update current user's profile."""
        if not self._current_user:
            return False, "No user logged in"

        username = self._current_user["username"]
        user = self._users.get(username)

        if not user:
            return False, "User not found"

        if display_name:
            user["display_name"] = display_name
            self._current_user["display_name"] = display_name

        if email:
            user["email"] = email
            self._current_user["email"] = email

        self._save_users()
        self._save_current_user()

        return True, "Profile updated"

    def change_password(self, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change current user's password."""
        if not self._current_user:
            return False, "No user logged in"

        username = self._current_user["username"]
        user = self._users.get(username)

        if not user:
            return False, "User not found"

        # Verify old password
        if not self._verify_password(old_password, user["password_hash"], user["password_salt"]):
            return False, "Invalid current password"

        # Validate new password
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"

        # Hash new password
        hashed, salt = self._hash_password(new_password)
        user["password_hash"] = hashed
        user["password_salt"] = salt

        self._save_users()

        return True, "Password changed successfully"

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self._preferences.get(key, default)

    def set_preference(self, key: str, value: Any):
        """Set a user preference."""
        self._preferences[key] = value
        self._save_preferences()

        # Also save to user profile
        if self._current_user:
            username = self._current_user["username"]
            if username in self._users:
                self._users[username]["preferences"] = self._preferences
                self._save_users()

    def get_all_preferences(self) -> dict[str, Any]:
        """Get all user preferences."""
        return self._preferences.copy()

    def delete_user(self, username: str, password: str) -> tuple[bool, str]:
        """Delete a user account."""
        username = username.strip().lower()

        if username not in self._users:
            return False, "User not found"

        user = self._users[username]

        # Verify password
        if not self._verify_password(password, user["password_hash"], user["password_salt"]):
            return False, "Invalid password"

        # Remove user
        del self._users[username]
        self._save_users()

        # Logout if this was the current user
        if self._current_user and self._current_user["username"] == username:
            self.logout()

        return True, "User deleted"

    def get_user_count(self) -> int:
        """Get the number of registered users."""
        return len(self._users)

    def get_user_info(self, username: str) -> Optional[dict[str, Any]]:
        """Get user info (without sensitive data)."""
        username = username.strip().lower()
        user = self._users.get(username)

        if not user:
            return None

        return {
            "username": user["username"],
            "display_name": user["display_name"],
            "email": user.get("email"),
            "created_at": user["created_at"],
            "last_login": user.get("last_login"),
            "login_count": user.get("login_count", 0),
        }


def get_user_manager() -> UserManager:
    """Get or create the global UserManager instance."""
    if not hasattr(get_user_manager, "_instance"):
        get_user_manager._instance = UserManager()
    return get_user_manager._instance

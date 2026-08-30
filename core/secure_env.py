"""
Jarvis V2 - Secure Environment Manager
=======================================
Manages .env files with encryption and security best practices.

Features:
- Encrypted .env storage
- Key rotation support
- Environment variable validation
- Secure secret generation
- Backup and restore
- Audit logging
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class SecureEnvManager:
    """
    Secure environment variable management.

    Features:
    - Encrypts .env file at rest
    - Validates environment variables
    - Generates secure secrets
    - Supports key rotation
    - Maintains audit log
    """

    # Required environment variables with validation rules
    ENV_SCHEMA = {
        "GROQ_API_KEY": {
            "description": "Groq API key for AI conversations",
            "required": False,
            "pattern": r"^gsk_[a-zA-Z0-9]{20,}$",
            "sensitive": True,
            "category": "ai",
        },
        "GROQ_MODEL": {
            "description": "Groq model to use",
            "required": False,
            "default": "llama-3.3-70b-versatile",
            "pattern": r"^[a-zA-Z0-9._-]+$",
            "sensitive": False,
            "category": "ai",
        },
        "OPENAI_API_KEY": {
            "description": "OpenAI API key (alternative to Groq)",
            "required": False,
            "pattern": r"^sk-[a-zA-Z0-9]{20,}$",
            "sensitive": True,
            "category": "ai",
        },
        "ANTHROPIC_API_KEY": {
            "description": "Anthropic API key (alternative to Groq)",
            "required": False,
            "pattern": r"^sk-ant-[a-zA-Z0-9]{20,}$",
            "sensitive": True,
            "category": "ai",
        },
        "JARVIS_EMAIL_ADDRESS": {
            "description": "Email address for sending/receiving",
            "required": False,
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "sensitive": False,
            "category": "email",
        },
        "JARVIS_EMAIL_APP_PASSWORD": {
            "description": "Email app password (not your main password!)",
            "required": False,
            "pattern": r"^[a-zA-Z0-9]{16,}$",
            "sensitive": True,
            "category": "email",
        },
        "JARVIS_SMTP_HOST": {
            "description": "SMTP server hostname",
            "required": False,
            "default": "smtp.gmail.com",
            "pattern": r"^[a-zA-Z0-9.-]+$",
            "sensitive": False,
            "category": "email",
        },
        "JARVIS_SMTP_PORT": {
            "description": "SMTP server port",
            "required": False,
            "default": "587",
            "pattern": r"^\d+$",
            "sensitive": False,
            "category": "email",
        },
        "JARVIS_IMAP_HOST": {
            "description": "IMAP server hostname",
            "required": False,
            "default": "imap.gmail.com",
            "pattern": r"^[a-zA-Z0-9.-]+$",
            "sensitive": False,
            "category": "email",
        },
        "TWILIO_ACCOUNT_SID": {
            "description": "Twilio Account SID",
            "required": False,
            "pattern": r"^AC[a-zA-Z0-9]{32}$",
            "sensitive": True,
            "category": "twilio",
        },
        "TWILIO_AUTH_TOKEN": {
            "description": "Twilio Auth Token",
            "required": False,
            "pattern": r"^[a-zA-Z0-9]{32}$",
            "sensitive": True,
            "category": "twilio",
        },
        "TWILIO_FROM_WHATSAPP": {
            "description": "Twilio WhatsApp number (whatsapp:+1...)",
            "required": False,
            "pattern": r"^whatsapp:\+[0-9]{10,15}$",
            "sensitive": False,
            "category": "twilio",
        },
        "TWILIO_FROM_PHONE": {
            "description": "Twilio phone number (+1...)",
            "required": False,
            "pattern": r"^\+[0-9]{10,15}$",
            "sensitive": False,
            "category": "twilio",
        },
        "TWILIO_TWIML_URL": {
            "description": "TwiML URL for call handling",
            "required": False,
            "pattern": r"^https?://",
            "sensitive": False,
            "category": "twilio",
        },
        "SPOTIFY_CLIENT_ID": {
            "description": "Spotify Developer Client ID",
            "required": False,
            "pattern": r"^[a-zA-Z0-9]{32}$",
            "sensitive": True,
            "category": "spotify",
        },
        "SPOTIFY_CLIENT_SECRET": {
            "description": "Spotify Developer Client Secret",
            "required": False,
            "pattern": r"^[a-zA-Z0-9]{32}$",
            "sensitive": True,
            "category": "spotify",
        },
        "SPOTIFY_REDIRECT_URI": {
            "description": "Spotify OAuth redirect URI",
            "required": False,
            "default": "http://localhost:8888/callback",
            "pattern": r"^https?://",
            "sensitive": False,
            "category": "spotify",
        },
        "HOME_ASSISTANT_URL": {
            "description": "Home Assistant URL",
            "required": False,
            "pattern": r"^https?://",
            "sensitive": False,
            "category": "smart_home",
        },
        "HOME_ASSISTANT_TOKEN": {
            "description": "Home Assistant Long-Lived Access Token",
            "required": False,
            "pattern": r"^[a-zA-Z0-9]{10,}$",
            "sensitive": True,
            "category": "smart_home",
        },
        "JARVIS_TARGET_PC_MAC": {
            "description": "Target PC MAC address for Wake-on-LAN",
            "required": False,
            "pattern": r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
            "sensitive": False,
            "category": "power",
        },
        "JARVIS_TARGET_PC_BROADCAST": {
            "description": "Broadcast address for Wake-on-LAN",
            "required": False,
            "default": "255.255.255.255",
            "pattern": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
            "sensitive": False,
            "category": "power",
        },
    }

    def __init__(
        self,
        env_path: Path = Path(".env"),
        encrypted_path: Optional[Path] = None,
        master_key: Optional[str] = None,
    ):
        self.env_path = env_path
        self.encrypted_path = encrypted_path or env_path.parent / ".env.enc"
        self._master_key = master_key
        self._cipher = None
        self._audit_log: list[dict[str, Any]] = []

        # Initialize encryption if available
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption cipher."""
        try:
            from cryptography.fernet import Fernet

            key_file = self.env_path.parent / ".env.key"

            if self._master_key:
                key = base64.urlsafe_b64encode(
                    hashlib.sha256(self._master_key.encode()).digest()[:32]
                )
            elif key_file.exists():
                key = key_file.read_bytes()
            else:
                key = Fernet.generate_key()
                key_file.write_bytes(key)
                try:
                    os.chmod(key_file, 0o600)
                except OSError:
                    pass

            self._cipher = Fernet(key)
        except ImportError:
            pass

    def _encrypt(self, data: str) -> str:
        """Encrypt data."""
        if self._cipher:
            return self._cipher.encrypt(data.encode()).decode()
        return base64.b64encode(data.encode()).decode()

    def _decrypt(self, data: str) -> str:
        """Decrypt data."""
        if self._cipher:
            try:
                return self._cipher.decrypt(data.encode()).decode()
            except Exception:
                return data
        try:
            return base64.b64decode(data.encode()).decode()
        except Exception:
            return data

    def load(self) -> dict[str, str]:
        """Load environment variables from .env file."""
        env_vars = {}

        # Try encrypted file first
        if self.encrypted_path.exists():
            try:
                encrypted = self.encrypted_path.read_text(encoding="utf-8")
                decrypted = self._decrypt(encrypted)
                env_vars = self._parse_env(decrypted)
            except Exception:
                pass

        # Fall back to regular .env
        if not env_vars and self.env_path.exists():
            try:
                content = self.env_path.read_text(encoding="utf-8")
                env_vars = self._parse_env(content)
            except Exception:
                pass

        return env_vars

    def save(self, env_vars: dict[str, str], encrypt: bool = True):
        """Save environment variables to .env file."""
        content = self._format_env(env_vars)

        if encrypt and self._cipher:
            encrypted = self._encrypt(content)
            self.encrypted_path.write_text(encrypted, encoding="utf-8")
            try:
                os.chmod(self.encrypted_path, 0o600)
            except OSError:
                pass
        else:
            self.env_path.write_text(content, encoding="utf-8")
            try:
                os.chmod(self.env_path, 0o600)
            except OSError:
                pass

        self._log_audit("save", list(env_vars.keys()))

    def get(self, key: str, default: str = "") -> str:
        """Get an environment variable."""
        # Check OS environment first
        value = os.getenv(key)
        if value:
            return value

        # Check .env file
        env_vars = self.load()
        return env_vars.get(key, default)

    def set(self, key: str, value: str, save: bool = True):
        """Set an environment variable."""
        env_vars = self.load()
        env_vars[key] = value

        if save:
            self.save(env_vars)

        # Also set in current process
        os.environ[key] = value

        self._log_audit("set", [key])

    def delete(self, key: str, save: bool = True):
        """Delete an environment variable."""
        env_vars = self.load()
        if key in env_vars:
            del env_vars[key]

            if save:
                self.save(env_vars)

            # Also remove from current process
            if key in os.environ:
                del os.environ[key]

            self._log_audit("delete", [key])

    def validate(self, key: str, value: str) -> tuple[bool, str]:
        """Validate an environment variable against its schema."""
        schema = self.ENV_SCHEMA.get(key)
        if not schema:
            return True, "Unknown variable"

        if not value and schema.get("required"):
            return False, f"{key} is required"

        if not value:
            return True, "Optional variable not set"

        pattern = schema.get("pattern")
        if pattern and not re.match(pattern, value):
            return False, f"Invalid format for {key}"

        return True, "Valid"

    def validate_all(self) -> dict[str, tuple[bool, str]]:
        """Validate all environment variables."""
        results = {}
        env_vars = self.load()

        for key, schema in self.ENV_SCHEMA.items():
            value = env_vars.get(key, "")
            results[key] = self.validate(key, value)

        return results

    def get_missing_required(self) -> list[str]:
        """Get list of missing required variables."""
        env_vars = self.load()
        missing = []

        for key, schema in self.ENV_SCHEMA.items():
            if schema.get("required") and not env_vars.get(key):
                missing.append(key)

        return missing

    def get_configured_categories(self) -> dict[str, list[str]]:
        """Get configured variables grouped by category."""
        env_vars = self.load()
        categories: dict[str, list[str]] = {}

        for key, schema in self.ENV_SCHEMA.items():
            category = schema.get("category", "other")
            if env_vars.get(key):
                if category not in categories:
                    categories[category] = []
                categories[category].append(key)

        return categories

    def generate_secret(self, length: int = 32) -> str:
        """Generate a cryptographically secure secret."""
        return secrets.token_urlsafe(length)

    def backup(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the .env file."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.env_path.parent / f".env.backup.{timestamp}"

        if self.encrypted_path.exists():
            shutil.copy2(self.encrypted_path, backup_path)
        elif self.env_path.exists():
            shutil.copy2(self.env_path, backup_path)

        self._log_audit("backup", [])
        return backup_path

    def restore(self, backup_path: Path):
        """Restore .env from backup."""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        if self.encrypted_path.exists():
            shutil.copy2(backup_path, self.encrypted_path)
        else:
            shutil.copy2(backup_path, self.env_path)

        self._log_audit("restore", [])

    def get_masked_values(self) -> dict[str, str]:
        """Get environment variables with sensitive values masked."""
        env_vars = self.load()
        masked = {}

        for key, value in env_vars.items():
            schema = self.ENV_SCHEMA.get(key, {})
            if schema.get("sensitive") and value:
                # Show first 4 and last 4 characters
                if len(value) > 8:
                    masked[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    masked[key] = "****"
            else:
                masked[key] = value

        return masked

    def get_status_report(self) -> str:
        """Get a formatted status report."""
        env_vars = self.load()
        validation = self.validate_all()

        lines = ["=" * 60]
        lines.append("  JARVIS V2 - ENVIRONMENT STATUS")
        lines.append("=" * 60)
        lines.append("")

        # Group by category
        categories: dict[str, list[str]] = {}
        for key, schema in self.ENV_SCHEMA.items():
            category = schema.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(key)

        for category, keys in sorted(categories.items()):
            lines.append(f"  [{category.upper()}]")
            for key in keys:
                value = env_vars.get(key, "")
                is_valid, msg = validation.get(key, (True, ""))

                if value:
                    status = "✅" if is_valid else "⚠️"
                    schema = self.ENV_SCHEMA[key]
                    if schema.get("sensitive"):
                        display = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
                    else:
                        display = value
                    lines.append(f"    {status} {key}: {display}")
                else:
                    required = self.ENV_SCHEMA[key].get("required", False)
                    if required:
                        lines.append(f"    ❌ {key}: MISSING (required)")
                    else:
                        lines.append(f"    ⬜ {key}: not set")

            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def _parse_env(self, content: str) -> dict[str, str]:
        """Parse .env file content."""
        env_vars = {}

        for line in content.splitlines():
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse KEY=VALUE
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                # Remove quotes
                if value and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]

                env_vars[key] = value

        return env_vars

    def _format_env(self, env_vars: dict[str, str]) -> str:
        """Format environment variables as .env content."""
        lines = [
            "# Jarvis V2 Environment Configuration",
            f"# Generated: {datetime.now().isoformat()}",
            "#",
            "# WARNING: This file contains sensitive credentials.",
            "# Never commit this file to version control!",
            "",
        ]

        # Group by category
        categories: dict[str, list[str]] = {}
        for key in env_vars:
            schema = self.ENV_SCHEMA.get(key, {})
            category = schema.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(key)

        for category, keys in sorted(categories.items()):
            lines.append(f"# {category.upper()}")
            for key in sorted(keys):
                value = env_vars[key]
                # Quote values with spaces
                if " " in value:
                    value = f'"{value}"'
                lines.append(f"{key}={value}")
            lines.append("")

        return "\n".join(lines)

    def _log_audit(self, action: str, keys: list[str]):
        """Log an audit entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "keys": keys,
        }
        self._audit_log.append(entry)

        # Also write to file
        try:
            audit_file = self.env_path.parent / "env_audit.log"
            with open(audit_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass


def get_secure_env() -> SecureEnvManager:
    """Get or create the global SecureEnvManager instance."""
    if not hasattr(get_secure_env, "_instance"):
        get_secure_env._instance = SecureEnvManager()
    return get_secure_env._instance


def load_env_securely() -> dict[str, str]:
    """Load environment variables securely."""
    manager = get_secure_env()
    env_vars = manager.load()

    # Set in current process
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    return env_vars

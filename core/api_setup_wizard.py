"""
Jarvis V2 - API Setup Wizard
=============================
Interactive wizard for configuring API integrations.

Features:
- Step-by-step guided setup
- API key validation
- Automatic .env generation
- Health check verification
- Configuration backup
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from .api_manager import APIManager, APIProvider
from .api_validator import APIValidator, ValidationResult, ValidationStatus
from .secure_env import SecureEnvManager


class APISetupWizard:
    """
    Interactive API setup wizard for Jarvis V2.

    Usage:
        wizard = APISetupWizard()
        wizard.run()
    """

    # API provider information
    PROVIDERS = {
        "groq": {
            "name": "Groq AI",
            "description": "Fast AI inference for conversations",
            "url": "https://console.groq.com",
            "env_vars": ["GROQ_API_KEY"],
            "instructions": [
                "1. Go to https://console.groq.com",
                "2. Sign up or log in",
                "3. Go to API Keys section",
                "4. Create a new API key",
                "5. Copy the key (starts with 'gsk_')",
            ],
            "required": False,
            "category": "ai",
        },
        "openai": {
            "name": "OpenAI",
            "description": "Alternative AI provider (GPT-4)",
            "url": "https://platform.openai.com",
            "env_vars": ["OPENAI_API_KEY"],
            "instructions": [
                "1. Go to https://platform.openai.com",
                "2. Sign up or log in",
                "3. Go to API Keys section",
                "4. Create a new secret key",
                "5. Copy the key (starts with 'sk-')",
            ],
            "required": False,
            "category": "ai",
        },
        "anthropic": {
            "name": "Anthropic",
            "description": "Alternative AI provider (Claude)",
            "url": "https://console.anthropic.com",
            "env_vars": ["ANTHROPIC_API_KEY"],
            "instructions": [
                "1. Go to https://console.anthropic.com",
                "2. Sign up or log in",
                "3. Go to API Keys section",
                "4. Create a new key",
                "5. Copy the key (starts with 'sk-ant-')",
            ],
            "required": False,
            "category": "ai",
        },
        "email": {
            "name": "Email (Gmail)",
            "description": "Send and receive emails",
            "url": "https://myaccount.google.com/apppasswords",
            "env_vars": [
                "JARVIS_EMAIL_ADDRESS",
                "JARVIS_EMAIL_APP_PASSWORD",
            ],
            "instructions": [
                "1. Enable 2-Factor Authentication on your Google account",
                "2. Go to https://myaccount.google.com/apppasswords",
                "3. Select 'Mail' and your device",
                "4. Click 'Generate'",
                "5. Copy the 16-character password",
                "6. Use your Gmail address as JARVIS_EMAIL_ADDRESS",
            ],
            "required": False,
            "category": "email",
        },
        "twilio": {
            "name": "Twilio (WhatsApp & Phone)",
            "description": "Send WhatsApp messages and make phone calls",
            "url": "https://console.twilio.com",
            "env_vars": [
                "TWILIO_ACCOUNT_SID",
                "TWILIO_AUTH_TOKEN",
                "TWILIO_FROM_WHATSAPP",
                "TWILIO_FROM_PHONE",
            ],
            "instructions": [
                "1. Go to https://console.twilio.com",
                "2. Sign up for a free account",
                "3. Find your Account SID and Auth Token on the dashboard",
                "4. Get a phone number from Phone Numbers section",
                "5. For WhatsApp, enable WhatsApp Sandbox in Messaging section",
            ],
            "required": False,
            "category": "twilio",
        },
        "spotify": {
            "name": "Spotify",
            "description": "Control music playback",
            "url": "https://developer.spotify.com/dashboard",
            "env_vars": [
                "SPOTIFY_CLIENT_ID",
                "SPOTIFY_CLIENT_SECRET",
            ],
            "instructions": [
                "1. Go to https://developer.spotify.com/dashboard",
                "2. Log in with your Spotify account",
                "3. Click 'Create App'",
                "4. Fill in app name and description",
                "5. Set Redirect URI to: http://localhost:8888/callback",
                "6. Copy Client ID and Client Secret",
            ],
            "required": False,
            "category": "spotify",
        },
        "home_assistant": {
            "name": "Home Assistant",
            "description": "Control smart home devices",
            "url": "http://homeassistant.local:8123/profile",
            "env_vars": [
                "HOME_ASSISTANT_URL",
                "HOME_ASSISTANT_TOKEN",
            ],
            "instructions": [
                "1. Open your Home Assistant dashboard",
                "2. Go to your Profile (click your name)",
                "3. Scroll to 'Long-Lived Access Tokens'",
                "4. Click 'Create Token'",
                "5. Give it a name like 'Jarvis V2'",
                "6. Copy the token immediately (shown only once!)",
            ],
            "required": False,
            "category": "smart_home",
        },
    }

    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.env_manager = SecureEnvManager()
        self.api_manager = APIManager(config_dir)
        self.validator = APIValidator()

    def run(self):
        """Run the interactive setup wizard."""
        self._print_header()

        while True:
            choice = self._show_menu()

            if choice == "1":
                self._setup_all()
            elif choice == "2":
                self._setup_single()
            elif choice == "3":
                self._validate_all()
            elif choice == "4":
                self._show_status()
            elif choice == "5":
                self._show_env()
            elif choice == "6":
                self._backup_config()
            elif choice == "7":
                self._restore_config()
            elif choice == "8":
                print("\nGoodbye, sir. All systems standing by.\n")
                break
            else:
                print("\nInvalid choice. Please try again.\n")

    def _print_header(self):
        """Print the wizard header."""
        print("\n" + "=" * 60)
        print("  JARVIS V2 - API SETUP WIZARD")
        print("=" * 60)
        print("\n  Configure all API integrations for maximum capability.")
        print("  Sensitive values are stored securely.\n")
        print("=" * 60 + "\n")

    def _show_menu(self) -> str:
        """Show the main menu."""
        print("\n  MAIN MENU")
        print("  " + "-" * 40)
        print("  1. Setup all APIs (guided)")
        print("  2. Setup specific API")
        print("  3. Validate all API keys")
        print("  4. Show API status")
        print("  5. Show environment variables")
        print("  6. Backup configuration")
        print("  7. Restore configuration")
        print("  8. Exit")
        print("  " + "-" * 40)

        return input("\n  Enter choice (1-8): ").strip()

    def _setup_all(self):
        """Setup all APIs interactively."""
        print("\n" + "=" * 60)
        print("  SETUP ALL APIs")
        print("=" * 60)
        print("\n  This will guide you through setting up each API integration.")
        print("  Press Enter to skip any optional API.\n")

        for provider_id, provider_info in self.PROVIDERS.items():
            self._setup_provider(provider_id, provider_info)

        print("\n" + "=" * 60)
        print("  SETUP COMPLETE!")
        print("=" * 60)
        print("\n  Run 'Validate all API keys' to verify your configuration.\n")

    def _setup_single(self):
        """Setup a single API."""
        print("\n  AVAILABLE APIs:")
        print("  " + "-" * 40)

        providers = list(self.PROVIDERS.items())
        for i, (provider_id, info) in enumerate(providers, 1):
            configured = "✓" if self.api_manager.has_credentials(
                APIProvider(provider_id)
            ) else " "
            print(f"  {i}. [{configured}] {info['name']}")

        print(f"  {len(providers) + 1}. Back to main menu")
        print("  " + "-" * 40)

        choice = input("\n  Select API to configure: ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(providers):
                provider_id, provider_info = providers[idx]
                self._setup_provider(provider_id, provider_info)
            elif idx == len(providers):
                return
            else:
                print("\n  Invalid choice.")
        except ValueError:
            print("\n  Invalid input.")

    def _setup_provider(self, provider_id: str, provider_info: dict):
        """Setup a single provider."""
        print(f"\n  {'=' * 50}")
        print(f"  {provider_info['name']}")
        print(f"  {provider_info['description']}")
        print(f"  {'=' * 50}")

        # Show instructions
        print(f"\n  Setup instructions:")
        for instruction in provider_info["instructions"]:
            print(f"    {instruction}")

        print(f"\n  Get your credentials at: {provider_info['url']}")

        # Collect credentials
        env_values = {}
        for env_var in provider_info["env_vars"]:
            current = self.env_manager.get(env_var)
            if current:
                print(f"\n  Current {env_var}: {current[:4]}...{current[-4:]}")
                keep = input("  Keep this value? (Y/n): ").strip().lower()
                if keep != "n":
                    env_values[env_var] = current
                    continue

            value = input(f"\n  Enter {env_var} (or press Enter to skip): ").strip()
            if value:
                env_values[env_var] = value

        # Save if we have values
        if env_values:
            for key, value in env_values.items():
                self.env_manager.set(key, value, save=False)
            self.env_manager.save(self.env_manager.load())

            # Validate
            print("\n  Validating...")
            self._validate_provider(provider_id)

            print(f"\n  ✓ {provider_info['name']} configured successfully!")
        else:
            print(f"\n  Skipped {provider_info['name']}")

    def _validate_all(self):
        """Validate all configured APIs."""
        print("\n" + "=" * 60)
        print("  VALIDATING ALL APIs")
        print("=" * 60 + "\n")

        results = {}

        # Validate Groq
        groq_key = self.env_manager.get("GROQ_API_KEY")
        if groq_key:
            print("  Validating Groq AI...")
            results["groq"] = self.validator.validate_groq(groq_key)

        # Validate OpenAI
        openai_key = self.env_manager.get("OPENAI_API_KEY")
        if openai_key:
            print("  Validating OpenAI...")
            results["openai"] = self.validator.validate_openai(openai_key)

        # Validate Anthropic
        anthropic_key = self.env_manager.get("ANTHROPIC_API_KEY")
        if anthropic_key:
            print("  Validating Anthropic...")
            results["anthropic"] = self.validator.validate_anthropic(anthropic_key)

        # Validate Twilio
        twilio_sid = self.env_manager.get("TWILIO_ACCOUNT_SID")
        twilio_token = self.env_manager.get("TWILIO_AUTH_TOKEN")
        if twilio_sid and twilio_token:
            print("  Validating Twilio...")
            results["twilio"] = self.validator.validate_twilio(twilio_sid, twilio_token)

        # Validate Home Assistant
        ha_url = self.env_manager.get("HOME_ASSISTANT_URL")
        ha_token = self.env_manager.get("HOME_ASSISTANT_TOKEN")
        if ha_url and ha_token:
            print("  Validating Home Assistant...")
            results["home_assistant"] = self.validator.validate_home_assistant(ha_url, ha_token)

        # Print results
        print("\n  RESULTS:")
        print("  " + "-" * 50)

        for provider, result in results.items():
            status_icon = {
                ValidationStatus.VALID: "✅",
                ValidationStatus.INVALID: "❌",
                ValidationStatus.EXPIRED: "⏰",
                ValidationStatus.RATE_LIMITED: "🔄",
                ValidationStatus.NETWORK_ERROR: "🌐",
                ValidationStatus.UNKNOWN: "❓",
            }.get(result.status, "❓")

            print(f"  {status_icon} {provider.upper()}: {result.message}")
            if result.latency_ms:
                print(f"     Latency: {result.latency_ms:.0f}ms")

        if not results:
            print("  No APIs configured to validate.")

        print("\n  " + "-" * 50)

    def _validate_provider(self, provider_id: str):
        """Validate a single provider."""
        if provider_id == "groq":
            key = self.env_manager.get("GROQ_API_KEY")
            if key:
                result = self.validator.validate_groq(key)
                self._print_validation_result(result)
        elif provider_id == "openai":
            key = self.env_manager.get("OPENAI_API_KEY")
            if key:
                result = self.validator.validate_openai(key)
                self._print_validation_result(result)
        elif provider_id == "anthropic":
            key = self.env_manager.get("ANTHROPIC_API_KEY")
            if key:
                result = self.validator.validate_anthropic(key)
                self._print_validation_result(result)
        elif provider_id == "twilio":
            sid = self.env_manager.get("TWILIO_ACCOUNT_SID")
            token = self.env_manager.get("TWILIO_AUTH_TOKEN")
            if sid and token:
                result = self.validator.validate_twilio(sid, token)
                self._print_validation_result(result)
        elif provider_id == "home_assistant":
            url = self.env_manager.get("HOME_ASSISTANT_URL")
            token = self.env_manager.get("HOME_ASSISTANT_TOKEN")
            if url and token:
                result = self.validator.validate_home_assistant(url, token)
                self._print_validation_result(result)

    def _print_validation_result(self, result: ValidationResult):
        """Print a validation result."""
        status_icon = {
            ValidationStatus.VALID: "✅",
            ValidationStatus.INVALID: "❌",
            ValidationStatus.EXPIRED: "⏰",
            ValidationStatus.RATE_LIMITED: "🔄",
            ValidationStatus.NETWORK_ERROR: "🌐",
            ValidationStatus.UNKNOWN: "❓",
        }.get(result.status, "❓")

        print(f"  {status_icon} {result.message}")

    def _show_status(self):
        """Show API status."""
        print("\n" + self.validator.get_status_report())

    def _show_env(self):
        """Show environment variables."""
        print("\n" + self.env_manager.get_status_report())

    def _backup_config(self):
        """Backup configuration."""
        backup_path = self.env_manager.backup()
        print(f"\n  ✓ Configuration backed up to: {backup_path}")

    def _restore_config(self):
        """Restore configuration from backup."""
        # List backups
        backup_dir = Path(".")
        backups = list(backup_dir.glob(".env.backup.*"))

        if not backups:
            print("\n  No backups found.")
            return

        print("\n  AVAILABLE BACKUPS:")
        for i, backup in enumerate(backups, 1):
            print(f"  {i}. {backup.name}")

        choice = input("\n  Select backup to restore (or press Enter to cancel): ").strip()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(backups):
                self.env_manager.restore(backups[idx])
                print(f"\n  ✓ Configuration restored from: {backups[idx].name}")
            else:
                print("\n  Cancelled.")
        except ValueError:
            print("\n  Cancelled.")


def run_setup_wizard():
    """Run the API setup wizard."""
    wizard = APISetupWizard()
    wizard.run()


if __name__ == "__main__":
    run_setup_wizard()

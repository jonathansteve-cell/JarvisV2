"""
Jarvis V2 - First-Run Setup Wizard
====================================
Interactive wizard for initial configuration and user registration.

Features:
- Welcome screen
- User registration
- API key configuration
- Voice setup
- Preferences configuration
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from .user_manager import UserManager, get_user_manager
from .api_manager import APIManager, APIProvider
from .api_validator import APIValidator
from .secure_env import SecureEnvManager


class SetupWizard:
    """
    First-run setup wizard for Jarvis V2.

    Guides users through:
    1. Welcome and introduction
    2. User registration
    3. API key configuration
    4. Voice and preferences setup
    """

    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.user_manager = get_user_manager()
        self.env_manager = SecureEnvManager()
        self.api_manager = APIManager(config_dir)
        self.validator = APIValidator()

    def run(self) -> bool:
        """
        Run the setup wizard.

        Returns:
            True if setup completed successfully, False otherwise
        """
        self._print_welcome()

        # Step 1: User Registration
        if not self._register_user():
            return False

        # Step 2: API Configuration
        self._configure_apis()

        # Step 3: Voice Setup
        self._configure_voice()

        # Step 4: Final Setup
        self._finalize_setup()

        return True

    def _print_welcome(self):
        """Print welcome message."""
        print("\n" + "=" * 60)
        print("  ╔══════════════════════════════════════════════════════════╗")
        print("  ║                                                          ║")
        print("  ║           WELCOME TO JARVIS V2 SETUP                     ║")
        print("  ║                                                          ║")
        print("  ║   All-in-One Desktop AI Assistant                        ║")
        print("  ║   Solar Core HUD · Voice Control · 19 Modules            ║")
        print("  ║                                                          ║")
        print("  ╚══════════════════════════════════════════════════════════╝")
        print("=" * 60)
        print("\n  This wizard will guide you through the initial setup.")
        print("  You'll create your account and configure Jarvis.")
        print("\n  Let's get started!\n")
        print("=" * 60 + "\n")

    def _register_user(self) -> bool:
        """Register the first user."""
        print("\n" + "-" * 60)
        print("  STEP 1: CREATE YOUR ACCOUNT")
        print("-" * 60)
        print("\n  Create your Jarvis account to personalize your experience.")
        print("  This will be your identity within Jarvis.\n")

        while True:
            # Get username
            username = input("  Enter a username (3-30 characters): ").strip()
            if not username:
                print("  [ERROR] Username cannot be empty.\n")
                continue
            if len(username) < 3:
                print("  [ERROR] Username must be at least 3 characters.\n")
                continue
            if len(username) > 30:
                print("  [ERROR] Username must be 30 characters or less.\n")
                continue

            # Get display name
            display_name = input("  Enter your display name (or press Enter for username): ").strip()
            if not display_name:
                display_name = username

            # Get email (optional)
            email = input("  Enter your email (optional, press Enter to skip): ").strip()
            if email and "@" not in email:
                print("  [WARN] Invalid email format. Skipping.\n")
                email = ""

            # Get password
            print("\n  Password requirements:")
            print("    - At least 8 characters")
            print("    - Mix of letters, numbers, and symbols recommended")
            print()

            password = input("  Enter your password: ").strip()
            if len(password) < 8:
                print("  [ERROR] Password must be at least 8 characters.\n")
                continue

            confirm_password = input("  Confirm your password: ").strip()
            if password != confirm_password:
                print("  [ERROR] Passwords do not match.\n")
                continue

            # Register user
            success, message = self.user_manager.register_user(
                username=username,
                password=password,
                display_name=display_name,
                email=email if email else None,
            )

            if success:
                print(f"\n  ✓ {message}")
                print(f"  Welcome, {display_name}!")

                # Auto-login
                self.user_manager.login(username, password)
                return True
            else:
                print(f"\n  [ERROR] {message}\n")
                continue

    def _configure_apis(self):
        """Configure API keys."""
        print("\n" + "-" * 60)
        print("  STEP 2: CONFIGURE API KEYS")
        print("-" * 60)
        print("\n  Jarvis uses APIs for advanced features.")
        print("  You can configure them now or skip and add later.\n")

        # Groq AI (recommended)
        print("  ┌─────────────────────────────────────────────────────────┐")
        print("  │  GROQ AI (Recommended - Fastest, Free)                  │")
        print("  │  Get your key at: https://console.groq.com              │")
        print("  └─────────────────────────────────────────────────────────┘")

        configure_groq = input("\n  Configure Groq AI now? (Y/n): ").strip().lower()
        if configure_groq != "n":
            self._setup_groq()

        # Email (optional)
        print("\n  ┌─────────────────────────────────────────────────────────┐")
        print("  │  EMAIL (Optional - Send/Receive Emails)                 │")
        print("  │  Requires Gmail with 2FA enabled                        │")
        print("  └─────────────────────────────────────────────────────────┘")

        configure_email = input("\n  Configure Email now? (y/N): ").strip().lower()
        if configure_email == "y":
            self._setup_email()

        # Twilio (optional)
        print("\n  ┌─────────────────────────────────────────────────────────┐")
        print("  │  TWILIO (Optional - WhatsApp & Phone)                   │")
        print("  │  Get credentials at: https://console.twilio.com         │")
        print("  └─────────────────────────────────────────────────────────┘")

        configure_twilio = input("\n  Configure Twilio now? (y/N): ").strip().lower()
        if configure_twilio == "y":
            self._setup_twilio()

        # Spotify (optional)
        print("\n  ┌─────────────────────────────────────────────────────────┐")
        print("  │  SPOTIFY (Optional - Music Control)                     │")
        print("  │  Get credentials at: https://developer.spotify.com      │")
        print("  └─────────────────────────────────────────────────────────┘")

        configure_spotify = input("\n  Configure Spotify now? (y/N): ").strip().lower()
        if configure_spotify == "y":
            self._setup_spotify()

    def _setup_groq(self):
        """Setup Groq AI."""
        print("\n  To get your Groq API key:")
        print("    1. Go to https://console.groq.com")
        print("    2. Sign up or log in")
        print("    3. Go to API Keys")
        print("    4. Create a new key")
        print("    5. Copy the key (starts with 'gsk_')")

        api_key = input("\n  Enter your GROQ_API_KEY: ").strip()
        if api_key:
            self.env_manager.set("GROQ_API_KEY", api_key)
            print("  ✓ Groq API key saved!")

            # Validate
            print("  Validating...")
            result = self.validator.validate_groq(api_key)
            if result.status.value == "valid":
                print(f"  ✓ Valid! Latency: {result.latency_ms:.0f}ms")
            else:
                print(f"  ⚠ {result.message}")
        else:
            print("  Skipped.")

    def _setup_email(self):
        """Setup Email."""
        print("\n  To setup Gmail:")
        print("    1. Enable 2-Factor Authentication on Google")
        print("    2. Go to https://myaccount.google.com/apppasswords")
        print("    3. Generate an App Password for 'Mail'")

        email = input("\n  Enter your Gmail address: ").strip()
        if not email:
            print("  Skipped.")
            return

        password = input("  Enter your App Password: ").strip()
        if not password:
            print("  Skipped.")
            return

        self.env_manager.set("JARVIS_EMAIL_ADDRESS", email, save=False)
        self.env_manager.set("JARVIS_EMAIL_APP_PASSWORD", password, save=False)
        self.env_manager.set("JARVIS_SMTP_HOST", "smtp.gmail.com", save=False)
        self.env_manager.set("JARVIS_SMTP_PORT", "587", save=False)
        self.env_manager.set("JARVIS_IMAP_HOST", "imap.gmail.com", save=False)
        self.env_manager.save(self.env_manager.load())

        print("  ✓ Email configured!")

    def _setup_twilio(self):
        """Setup Twilio."""
        print("\n  To get Twilio credentials:")
        print("    1. Go to https://console.twilio.com")
        print("    2. Sign up for free ($15 credit)")
        print("    3. Find Account SID and Auth Token on dashboard")

        sid = input("\n  Enter TWILIO_ACCOUNT_SID: ").strip()
        if not sid:
            print("  Skipped.")
            return

        token = input("  Enter TWILIO_AUTH_TOKEN: ").strip()
        if not token:
            print("  Skipped.")
            return

        phone = input("  Enter TWILIO_FROM_PHONE (e.g., +1234567890): ").strip()
        whatsapp = input("  Enter TWILIO_FROM_WHATSAPP (e.g., whatsapp:+14155238886): ").strip()

        self.env_manager.set("TWILIO_ACCOUNT_SID", sid, save=False)
        self.env_manager.set("TWILIO_AUTH_TOKEN", token, save=False)
        if phone:
            self.env_manager.set("TWILIO_FROM_PHONE", phone, save=False)
        if whatsapp:
            self.env_manager.set("TWILIO_FROM_WHATSAPP", whatsapp, save=False)
        self.env_manager.save(self.env_manager.load())

        print("  ✓ Twilio configured!")

    def _setup_spotify(self):
        """Setup Spotify."""
        print("\n  To get Spotify credentials:")
        print("    1. Go to https://developer.spotify.com/dashboard")
        print("    2. Create a new app")
        print("    3. Set Redirect URI to: http://localhost:8888/callback")

        client_id = input("\n  Enter SPOTIFY_CLIENT_ID: ").strip()
        if not client_id:
            print("  Skipped.")
            return

        client_secret = input("  Enter SPOTIFY_CLIENT_SECRET: ").strip()
        if not client_secret:
            print("  Skipped.")
            return

        self.env_manager.set("SPOTIFY_CLIENT_ID", client_id, save=False)
        self.env_manager.set("SPOTIFY_CLIENT_SECRET", client_secret, save=False)
        self.env_manager.set("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback", save=False)
        self.env_manager.save(self.env_manager.load())

        print("  ✓ Spotify configured!")

    def _configure_voice(self):
        """Configure voice settings."""
        print("\n" + "-" * 60)
        print("  STEP 3: VOICE SETTINGS")
        print("-" * 60)
        print("\n  Jarvis can speak responses using text-to-speech.")
        print("  Choose your preferred voice style:\n")

        print("  1. Dark Synthetic (Default) - Slow, low, commanding")
        print("  2. Jarvis Classic - Calm, polite, professional")
        print("  3. Fast Operator - Brisk, mission-control pace")
        print("  4. Gentle - Softer, quieter voice")

        choice = input("\n  Select voice (1-4, or press Enter for default): ").strip()

        voice_profiles = {
            "1": "dark_synthetic",
            "2": "jarvis_classic",
            "3": "fast_operator",
            "4": "gentle",
        }

        profile = voice_profiles.get(choice, "dark_synthetic")
        self.user_manager.set_preference("voice_profile", profile)
        print(f"  ✓ Voice set to: {profile}")

        # TTS Engine
        print("\n  TTS Engine options:")
        print("  1. Auto (best available)")
        print("  2. Edge Neural (natural, requires internet)")
        print("  3. pyttsx3 (offline, robotic)")
        print("  4. System (OS default)")

        engine_choice = input("\n  Select engine (1-4, or press Enter for auto): ").strip()

        engines = {
            "1": "auto",
            "2": "edge",
            "3": "pyttsx3",
            "4": "system",
        }

        engine = engines.get(engine_choice, "auto")
        self.user_manager.set_preference("tts_engine", engine)
        print(f"  ✓ TTS engine set to: {engine}")

    def _finalize_setup(self):
        """Finalize setup."""
        print("\n" + "-" * 60)
        print("  STEP 4: SETUP COMPLETE!")
        print("-" * 60)

        user = self.user_manager.get_current_user()
        display_name = user["display_name"] if user else "User"

        print(f"\n  ✓ Welcome, {display_name}!")
        print("\n  Your Jarvis V2 is now configured and ready to use.")
        print("\n  ┌─────────────────────────────────────────────────────────┐")
        print("  │  QUICK START GUIDE                                      │")
        print("  ├─────────────────────────────────────────────────────────┤")
        print("  │                                                         │")
        print("  │  • Type commands in the chat box                        │")
        print("  │  • Click SPEAK for voice commands                       │")
        print("  │  • Say 'Hey Jarvis' to activate voice                   │")
        print("  │  • Try: 'What can you do?'                              │")
        print("  │  • Try: 'System status'                                 │")
        print("  │  • Try: 'Tell me a joke'                                │")
        print("  │                                                         │")
        print("  └─────────────────────────────────────────────────────────┘")

        print("\n  Configuration saved to:")
        print("    • User data: data/users.json")
        print("    • API keys: .env (encrypted)")
        print("    • Preferences: data/user_preferences.json")

        print("\n" + "=" * 60)
        print("  Starting Jarvis V2...")
        print("=" * 60 + "\n")


def run_setup_wizard() -> bool:
    """Run the setup wizard if needed."""
    user_manager = get_user_manager()

    if user_manager.is_first_run():
        wizard = SetupWizard()
        return wizard.run()

    return True


def check_and_login() -> bool:
    """Check if user is logged in, prompt for login if needed."""
    user_manager = get_user_manager()

    if user_manager.is_logged_in():
        return True

    if not user_manager.has_users():
        # First run - need to register
        wizard = SetupWizard()
        return wizard.run()

    # Existing user - prompt for login
    print("\n" + "=" * 60)
    print("  JARVIS V2 - LOGIN")
    print("=" * 60 + "\n")

    max_attempts = 3
    for attempt in range(max_attempts):
        username = input("  Username: ").strip()
        password = input("  Password: ").strip()

        success, message = user_manager.login(username, password)
        if success:
            user = user_manager.get_current_user()
            print(f"\n  ✓ Welcome back, {user['display_name']}!\n")
            return True
        else:
            remaining = max_attempts - attempt - 1
            print(f"\n  [ERROR] {message}")
            if remaining > 0:
                print(f"  {remaining} attempts remaining.\n")

    print("\n  [ERROR] Too many failed attempts.")
    return False

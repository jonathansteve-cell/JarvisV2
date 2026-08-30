#!/usr/bin/env python3
"""
Jarvis V2 - Quick API Setup Script
====================================
One-click setup for all API integrations.

Usage:
    python setup_apis.py
    python setup_apis.py --quick    # Skip validation
    python setup_apis.py --validate # Only validate existing config
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.api_manager import APIManager, APIProvider
from core.api_validator import APIValidator, ValidationStatus
from core.secure_env import SecureEnvManager


def print_header():
    """Print setup header."""
    print("\n" + "=" * 60)
    print("  JARVIS V2 - QUICK API SETUP")
    print("=" * 60)
    print("\n  This script will help you configure all API integrations.")
    print("  Press Enter to skip any optional API.\n")
    print("=" * 60 + "\n")


def setup_groq(env_manager: SecureEnvManager, validator: APIValidator) -> bool:
    """Setup Groq AI."""
    print("\n" + "-" * 50)
    print("  GROQ AI (Recommended - Fastest)")
    print("-" * 50)
    print("\n  Groq provides fast AI inference for conversations.")
    print("  Get your key at: https://console.groq.com")
    print("\n  Steps:")
    print("    1. Go to https://console.groq.com")
    print("    2. Sign up or log in")
    print("    3. Go to API Keys")
    print("    4. Create a new key")
    print("    5. Copy the key (starts with 'gsk_')")

    current = env_manager.get("GROQ_API_KEY")
    if current:
        print(f"\n  Current key: {current[:4]}...{current[-4:]}")
        keep = input("  Keep this key? (Y/n): ").strip().lower()
        if keep != "n":
            return True

    key = input("\n  Enter GROQ_API_KEY (or press Enter to skip): ").strip()
    if not key:
        print("  Skipped.")
        return False

    env_manager.set("GROQ_API_KEY", key)

    # Validate
    print("\n  Validating...")
    result = validator.validate_groq(key)

    if result.status == ValidationStatus.VALID:
        print(f"  ✅ Valid! Latency: {result.latency_ms:.0f}ms")
        return True
    else:
        print(f"  ❌ {result.message}")
        return False


def setup_openai(env_manager: SecureEnvManager, validator: APIValidator) -> bool:
    """Setup OpenAI."""
    print("\n" + "-" * 50)
    print("  OPENAI (Alternative - Most Capable)")
    print("-" * 50)
    print("\n  OpenAI provides GPT-4 and other models.")
    print("  Get your key at: https://platform.openai.com")

    current = env_manager.get("OPENAI_API_KEY")
    if current:
        print(f"\n  Current key: {current[:4]}...{current[-4:]}")
        keep = input("  Keep this key? (Y/n): ").strip().lower()
        if keep != "n":
            return True

    key = input("\n  Enter OPENAI_API_KEY (or press Enter to skip): ").strip()
    if not key:
        print("  Skipped.")
        return False

    env_manager.set("OPENAI_API_KEY", key)

    # Validate
    print("\n  Validating...")
    result = validator.validate_openai(key)

    if result.status == ValidationStatus.VALID:
        print(f"  ✅ Valid! Latency: {result.latency_ms:.0f}ms")
        return True
    else:
        print(f"  ❌ {result.message}")
        return False


def setup_anthropic(env_manager: SecureEnvManager, validator: APIValidator) -> bool:
    """Setup Anthropic."""
    print("\n" + "-" * 50)
    print("  ANTHROPIC (Alternative - Best for Safety)")
    print("-" * 50)
    print("\n  Anthropic provides Claude models.")
    print("  Get your key at: https://console.anthropic.com")

    current = env_manager.get("ANTHROPIC_API_KEY")
    if current:
        print(f"\n  Current key: {current[:4]}...{current[-4:]}")
        keep = input("  Keep this key? (Y/n): ").strip().lower()
        if keep != "n":
            return True

    key = input("\n  Enter ANTHROPIC_API_KEY (or press Enter to skip): ").strip()
    if not key:
        print("  Skipped.")
        return False

    env_manager.set("ANTHROPIC_API_KEY", key)

    # Validate
    print("\n  Validating...")
    result = validator.validate_anthropic(key)

    if result.status == ValidationStatus.VALID:
        print(f"  ✅ Valid! Latency: {result.latency_ms:.0f}ms")
        return True
    else:
        print(f"  ❌ {result.message}")
        return False


def setup_email(env_manager: SecureEnvManager) -> bool:
    """Setup Email."""
    print("\n" + "-" * 50)
    print("  EMAIL (Gmail)")
    print("-" * 50)
    print("\n  Send and receive emails with Jarvis.")
    print("  Requires Gmail with 2FA enabled.")
    print("\n  Steps:")
    print("    1. Enable 2-Factor Authentication on Google")
    print("    2. Go to https://myaccount.google.com/apppasswords")
    print("    3. Generate an App Password for 'Mail'")
    print("    4. Use that password below")

    current_email = env_manager.get("JARVIS_EMAIL_ADDRESS")
    if current_email:
        print(f"\n  Current email: {current_email}")
        keep = input("  Keep this? (Y/n): ").strip().lower()
        if keep != "n":
            return True

    email = input("\n  Enter JARVIS_EMAIL_ADDRESS (or press Enter to skip): ").strip()
    if not email:
        print("  Skipped.")
        return False

    password = input("  Enter JARVIS_EMAIL_APP_PASSWORD: ").strip()
    if not password:
        print("  Skipped (no password).")
        return False

    env_manager.set("JARVIS_EMAIL_ADDRESS", email, save=False)
    env_manager.set("JARVIS_EMAIL_APP_PASSWORD", password, save=False)
    env_manager.set("JARVIS_SMTP_HOST", "smtp.gmail.com", save=False)
    env_manager.set("JARVIS_SMTP_PORT", "587", save=False)
    env_manager.set("JARVIS_IMAP_HOST", "imap.gmail.com", save=False)
    env_manager.save(env_manager.load())

    print("  ✅ Email configured!")
    return True


def setup_twilio(env_manager: SecureEnvManager, validator: APIValidator) -> bool:
    """Setup Twilio."""
    print("\n" + "-" * 50)
    print("  TWILIO (WhatsApp & Phone)")
    print("-" * 50)
    print("\n  Send WhatsApp messages and make phone calls.")
    print("  Get credentials at: https://console.twilio.com")
    print("\n  Free trial includes $15 credit.")

    current_sid = env_manager.get("TWILIO_ACCOUNT_SID")
    if current_sid:
        print(f"\n  Current SID: {current_sid[:4]}...{current_sid[-4:]}")
        keep = input("  Keep these credentials? (Y/n): ").strip().lower()
        if keep != "n":
            return True

    sid = input("\n  Enter TWILIO_ACCOUNT_SID (or press Enter to skip): ").strip()
    if not sid:
        print("  Skipped.")
        return False

    token = input("  Enter TWILIO_AUTH_TOKEN: ").strip()
    if not token:
        print("  Skipped (no token).")
        return False

    phone = input("  Enter TWILIO_FROM_PHONE (e.g., +1234567890): ").strip()
    whatsapp = input("  Enter TWILIO_FROM_WHATSAPP (e.g., whatsapp:+14155238886): ").strip()

    env_manager.set("TWILIO_ACCOUNT_SID", sid, save=False)
    env_manager.set("TWILIO_AUTH_TOKEN", token, save=False)
    if phone:
        env_manager.set("TWILIO_FROM_PHONE", phone, save=False)
    if whatsapp:
        env_manager.set("TWILIO_FROM_WHATSAPP", whatsapp, save=False)
    env_manager.save(env_manager.load())

    # Validate
    print("\n  Validating...")
    result = validator.validate_twilio(sid, token)

    if result.status == ValidationStatus.VALID:
        print(f"  ✅ Valid! Latency: {result.latency_ms:.0f}ms")
        return True
    else:
        print(f"  ❌ {result.message}")
        return False


def setup_spotify(env_manager: SecureEnvManager) -> bool:
    """Setup Spotify."""
    print("\n" + "-" * 50)
    print("  SPOTIFY (Music Control)")
    print("-" * 50)
    print("\n  Control music playback with Jarvis.")
    print("  Get credentials at: https://developer.spotify.com/dashboard")
    print("\n  Steps:")
    print("    1. Create a Spotify Developer account")
    print("    2. Create a new app")
    print("    3. Set Redirect URI to: http://localhost:8888/callback")
    print("    4. Copy Client ID and Client Secret")

    current_id = env_manager.get("SPOTIFY_CLIENT_ID")
    if current_id:
        print(f"\n  Current Client ID: {current_id[:4]}...{current_id[-4:]}")
        keep = input("  Keep these credentials? (Y/n): ").strip().lower()
        if keep != "n":
            return True

    client_id = input("\n  Enter SPOTIFY_CLIENT_ID (or press Enter to skip): ").strip()
    if not client_id:
        print("  Skipped.")
        return False

    client_secret = input("  Enter SPOTIFY_CLIENT_SECRET: ").strip()
    if not client_secret:
        print("  Skipped (no secret).")
        return False

    env_manager.set("SPOTIFY_CLIENT_ID", client_id, save=False)
    env_manager.set("SPOTIFY_CLIENT_SECRET", client_secret, save=False)
    env_manager.set("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback", save=False)
    env_manager.save(env_manager.load())

    print("  ✅ Spotify configured!")
    return True


def setup_home_assistant(env_manager: SecureEnvManager, validator: APIValidator) -> bool:
    """Setup Home Assistant."""
    print("\n" + "-" * 50)
    print("  HOME ASSISTANT (Smart Home)")
    print("-" * 50)
    print("\n  Control smart home devices with Jarvis.")
    print("  Requires a running Home Assistant instance.")

    current_url = env_manager.get("HOME_ASSISTANT_URL")
    if current_url:
        print(f"\n  Current URL: {current_url}")
        keep = input("  Keep these settings? (Y/n): ").strip().lower()
        if keep != "n":
            return True

    url = input("\n  Enter HOME_ASSISTANT_URL (or press Enter to skip): ").strip()
    if not url:
        print("  Skipped.")
        return False

    token = input("  Enter HOME_ASSISTANT_TOKEN: ").strip()
    if not token:
        print("  Skipped (no token).")
        return False

    env_manager.set("HOME_ASSISTANT_URL", url, save=False)
    env_manager.set("HOME_ASSISTANT_TOKEN", token, save=False)
    env_manager.save(env_manager.load())

    # Validate
    print("\n  Validating...")
    result = validator.validate_home_assistant(url, token)

    if result.status == ValidationStatus.VALID:
        print(f"  ✅ Valid! Latency: {result.latency_ms:.0f}ms")
        return True
    else:
        print(f"  ❌ {result.message}")
        return False


def validate_existing(env_manager: SecureEnvManager, validator: APIValidator):
    """Validate existing configuration."""
    print("\n" + "=" * 60)
    print("  VALIDATING EXISTING CONFIGURATION")
    print("=" * 60 + "\n")

    results = {}

    # Groq
    groq_key = env_manager.get("GROQ_API_KEY")
    if groq_key:
        print("  Validating Groq AI...")
        results["groq"] = validator.validate_groq(groq_key)

    # OpenAI
    openai_key = env_manager.get("OPENAI_API_KEY")
    if openai_key:
        print("  Validating OpenAI...")
        results["openai"] = validator.validate_openai(openai_key)

    # Anthropic
    anthropic_key = env_manager.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("  Validating Anthropic...")
        results["anthropic"] = validator.validate_anthropic(anthropic_key)

    # Twilio
    twilio_sid = env_manager.get("TWILIO_ACCOUNT_SID")
    twilio_token = env_manager.get("TWILIO_AUTH_TOKEN")
    if twilio_sid and twilio_token:
        print("  Validating Twilio...")
        results["twilio"] = validator.validate_twilio(twilio_sid, twilio_token)

    # Home Assistant
    ha_url = env_manager.get("HOME_ASSISTANT_URL")
    ha_token = env_manager.get("HOME_ASSISTANT_TOKEN")
    if ha_url and ha_token:
        print("  Validating Home Assistant...")
        results["home_assistant"] = validator.validate_home_assistant(ha_url, ha_token)

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

    if not results:
        print("  No APIs configured to validate.")

    print("\n  " + "-" * 50)


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Jarvis V2 - Quick API Setup"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip validation",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Only validate existing configuration",
    )
    args = parser.parse_args()

    print_header()

    env_manager = SecureEnvManager()
    validator = APIValidator()

    if args.validate:
        validate_existing(env_manager, validator)
        return

    # Setup each API
    configured = []

    print("\n  Let's configure your API integrations.\n")

    # Groq (recommended)
    if setup_groq(env_manager, validator):
        configured.append("groq")

    # OpenAI (optional)
    print("\n  Would you like to configure OpenAI as a fallback? (y/N): ")
    if input().strip().lower() == "y":
        if setup_openai(env_manager, validator):
            configured.append("openai")

    # Anthropic (optional)
    print("\n  Would you like to configure Anthropic as a fallback? (y/N): ")
    if input().strip().lower() == "y":
        if setup_anthropic(env_manager, validator):
            configured.append("anthropic")

    # Email (optional)
    print("\n  Would you like to configure Email? (y/N): ")
    if input().strip().lower() == "y":
        if setup_email(env_manager):
            configured.append("email")

    # Twilio (optional)
    print("\n  Would you like to configure Twilio (WhatsApp/Phone)? (y/N): ")
    if input().strip().lower() == "y":
        if setup_twilio(env_manager, validator):
            configured.append("twilio")

    # Spotify (optional)
    print("\n  Would you like to configure Spotify? (y/N): ")
    if input().strip().lower() == "y":
        if setup_spotify(env_manager):
            configured.append("spotify")

    # Home Assistant (optional)
    print("\n  Would you like to configure Home Assistant? (y/N): ")
    if input().strip().lower() == "y":
        if setup_home_assistant(env_manager, validator):
            configured.append("home_assistant")

    # Summary
    print("\n" + "=" * 60)
    print("  SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n  Configured APIs: {', '.join(configured) if configured else 'none'}")
    print("\n  Your configuration has been saved to .env")
    print("  Run Jarvis with: python main.py")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()

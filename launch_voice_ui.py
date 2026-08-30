#!/usr/bin/env python3
"""
Jarvis V2 - Voice-Only UI Launcher
====================================
Launch the voice-only 3D interface.

Usage:
    python launch_voice_ui.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.voice_only_ui import VoiceOnlyUI


def main():
    """Launch the voice-only UI."""
    print("\n" + "=" * 60)
    print("  JARVIS V2 - VOICE AI INTERFACE")
    print("=" * 60)
    print("\n  Starting voice-only 3D interface...")
    print("  Use voice commands to interact with Jarvis.")
    print("  Close the window to exit.\n")
    print("=" * 60 + "\n")
    
    try:
        ui = VoiceOnlyUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
    except Exception as e:
        print(f"\n  Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

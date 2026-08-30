#!/usr/bin/env python3
"""
Jarvis V2 - Modern UI Launcher
================================
Launch the modern Jarvis V2 interface.

Usage:
    python launch_modern_ui.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.modern_ui import ModernJarvisUI


def main():
    """Launch the modern UI."""
    print("\n" + "=" * 60)
    print("  JARVIS V2 - MODERN UI")
    print("=" * 60)
    print("\n  Starting modern interface...")
    print("  Close the window to exit.\n")
    print("=" * 60 + "\n")
    
    try:
        ui = ModernJarvisUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
    except Exception as e:
        print(f"\n  Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

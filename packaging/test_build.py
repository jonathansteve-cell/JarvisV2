#!/usr/bin/env python3
"""
Test script to verify the build environment is ready.
Run this before building to check for common issues.
"""

import os
import sys
import shutil
from pathlib import Path

def check_python():
    """Check Python version."""
    print("[1/5] Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"  [FAIL] Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """Check pip is available."""
    print("[2/5] Checking pip...")
    try:
        import pip
        print(f"  [OK] pip {pip.__version__}")
        return True
    except ImportError:
        print("  [FAIL] pip not found")
        return False

def check_requirements():
    """Check if requirements.txt exists and is readable."""
    print("[3/5] Checking requirements.txt...")
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("  [FAIL] requirements.txt not found")
        return False
    
    try:
        requirements = req_file.read_text().strip().split('\n')
        requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]
        print(f"  [OK] Found {len(requirements)} dependencies")
        return True
    except Exception as e:
        print(f"  [FAIL] Error reading requirements.txt: {e}")
        return False

def check_packaging_files():
    """Check if packaging files exist."""
    print("[4/5] Checking packaging files...")
    
    required_files = [
        "packaging/jarvis.spec",
        "packaging/make_icon.py",
        "packaging/desktop_launcher.py",
        "packaging/app.png",
    ]
    
    missing = []
    for f in required_files:
        if not Path(f).exists():
            missing.append(f)
    
    if missing:
        print(f"  [FAIL] Missing files: {', '.join(missing)}")
        return False
    
    print("  [OK] All packaging files present")
    return True

def check_disk_space():
    """Check available disk space."""
    print("[5/5] Checking disk space...")
    
    try:
        # Get free space in bytes
        free_bytes = shutil.disk_usage('.').free
        free_mb = free_bytes / (1024 * 1024)
        
        # Need at least 500 MB for build
        if free_mb < 500:
            print(f"  [WARN] Low disk space: {free_mb:.0f} MB (recommend 500+ MB)")
            return True  # Warning, not failure
        
        print(f"  [OK] {free_mb:.0f} MB available")
        return True
    except Exception as e:
        print(f"  [WARN] Could not check disk space: {e}")
        return True

def main():
    """Run all checks."""
    print("=" * 60)
    print("  Jarvis V2 - Build Environment Check")
    print("=" * 60)
    print()
    
    checks = [
        check_python(),
        check_pip(),
        check_requirements(),
        check_packaging_files(),
        check_disk_space(),
    ]
    
    print()
    print("=" * 60)
    
    if all(checks):
        print("  [SUCCESS] All checks passed!")
        print()
        print("  You're ready to build. Run:")
        print("    packaging\\OneClickBuild.bat    (Windows)")
        print("    ./packaging/build_installer.sh  (macOS/Linux)")
        print("=" * 60)
        return 0
    else:
        print("  [FAILED] Some checks failed.")
        print()
        print("  Please fix the issues above before building.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

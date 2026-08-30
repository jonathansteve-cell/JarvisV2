#!/usr/bin/env python3
"""
Jarvis V2 - Installer Configuration Generator
==============================================
Generates platform-specific installer configurations and scripts.

Usage:
    python packaging/installer_generator.py [--platform windows|macos|linux|all]

This script generates:
- Windows: Inno Setup script (.iss) + build batch file
- macOS: DMG creation script + Info.plist for .app bundle
- Linux: AppImage structure + .desktop file + AppRun script
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from textwrap import dedent

# App metadata
APP_NAME = "Jarvis V2"
APP_NAME_SHORT = "JarvisV2"
APP_VERSION = "2.0.0"
APP_PUBLISHER = "jonathansteve-cell"
APP_URL = "https://github.com/jonathansteve-cell/JarvisV2"
APP_DESCRIPTION = "All-in-One Desktop AI Assistant - Solar Core HUD"
APP_ID = "8F3B2A9E-4C71-4C6B-9B2E-2D1A5E0F0C21"

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def generate_macos_app_bundle() -> None:
    """Generate macOS .app bundle structure."""
    bundle_dir = PROJECT / "dist" / f"{APP_NAME_SHORT}.app"
    contents = bundle_dir / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"

    for d in [bundle_dir, contents, macos, resources]:
        d.mkdir(parents=True, exist_ok=True)

    # Info.plist
    plist = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{APP_NAME_SHORT}</string>
    <key>CFBundleDisplayName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.{APP_PUBLISHER}.{APP_NAME_SHORT}</string>
    <key>CFBundleVersion</key>
    <string>{APP_VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>{APP_VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>{APP_NAME_SHORT}</string>
    <key>CFBundleIconFile</key>
    <string>app.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSMicrophoneUsageDescription</key>
    <string>Jarvis V2 needs microphone access for voice commands.</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
</dict>
</plist>
"""
    (contents / "Info.plist").write_text(plist)

    # Launcher script
    launcher = f"""\
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
CONTENTS="$(dirname "$DIR")"
APP_DIR="$(dirname "$CONTENTS")"
cd "$APP_DIR/../dist/{APP_NAME_SHORT}"
exec ./JarvisV2 "$@"
"""
    launcher_path = macos / APP_NAME_SHORT
    launcher_path.write_text(launcher)
    launcher_path.chmod(0o755)

    print(f"[OK] macOS .app bundle structure created at: {bundle_dir}")
    print(f"     Copy dist/{APP_NAME_SHORT}/ contents into {bundle_dir}/Contents/MacOS/")


def generate_linux_desktop() -> None:
    """Generate Linux .desktop file and AppImage structure."""
    appimage_dir = PROJECT / "dist" / f"{APP_NAME_SHORT}.AppDir"
    appimage_dir.mkdir(parents=True, exist_ok=True)

    # .desktop file
    desktop = f"""\
[Desktop Entry]
Type=Application
Name={APP_NAME}
GenericName=AI Assistant
Comment={APP_DESCRIPTION}
Exec=JarvisV2
Icon=app
Terminal=false
Categories=Utility;Office;
Keywords=ai;assistant;jarvis;voice;
StartupWMClass=JarvisV2
"""
    (appimage_dir / f"{APP_NAME_SHORT}.desktop").write_text(desktop)

    # AppRun script
    apprun = f"""\
#!/bin/bash
SELF="$(readlink -f "$0")"
HERE="${{SELF%/*}}"
export PATH="$HERE/usr/bin:$HERE/usr/sbin:$HERE/usr/games:$HERE/bin:$HERE/sbin:$PATH"
export LD_LIBRARY_PATH="$HERE/usr/lib:$HERE/usr/lib/x86_64-linux-gnu:$HERE/usr/lib/i386-linux-gnu:$LD_LIBRARY_PATH"
cd "$HERE/dist/{APP_NAME_SHORT}"
exec ./JarvisV2 "$@"
"""
    apprun_path = appimage_dir / "AppRun"
    apprun_path.write_text(apprun)
    apprun_path.chmod(0o755)

    # Copy icon
    icon_src = HERE / "app.png"
    if icon_src.exists():
        import shutil
        shutil.copy2(icon_src, appimage_dir / "app.png")

    print(f"[OK] Linux AppImage structure created at: {appimage_dir}")
    print(f"     To build: appimagetool {appimage_dir} dist/{APP_NAME_SHORT}.AppImage")


def generate_nsis_script() -> str:
    """Generate an NSIS installer script as an alternative to Inno Setup."""
    script = f"""\
; Jarvis V2 - NSIS Installer Script
; Alternative to Inno Setup for building Install.exe
; Build with: makensis packaging/installer.nsi

!include "MUI2.nsh"
!include "FileFunc.nsh"

; ----- Configuration -----
Name "{APP_NAME}"
OutFile "..\\dist\\installer\\{APP_NAME_SHORT}-Setup.exe"
InstallDir "$PROGRAMFILES\\{APP_NAME_SHORT}"
InstallDirRegKey HKLM "Software\\{APP_NAME_SHORT}" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

; ----- Version Info -----
VIProductVersion "{APP_VERSION}.0"
VIAddVersionKey "ProductName" "{APP_NAME}"
VIAddVersionKey "CompanyName" "{APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "{APP_DESCRIPTION}"
VIAddVersionKey "FileVersion" "{APP_VERSION}"
VIAddVersionKey "ProductVersion" "{APP_VERSION}"
VIAddVersionKey "LegalCopyright" "Copyright 2026 {APP_PUBLISHER}"

; ----- MUI Configuration -----
!define MUI_ABORTWARNING
!define MUI_ICON "app.ico"
!define MUI_UNICON "app.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "app.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "app.bmp"
!define MUI_HEADERIMAGE_RIGHT

; ----- Pages -----
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\\{APP_NAME_SHORT}.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch {APP_NAME}"
!define MUI_FINISHPAGE_LINK "Visit project on GitHub"
!define MUI_FINISHPAGE_LINK_LOCATION "{APP_URL}"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ----- Languages -----
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Japanese"

; ----- Installer Sections -----
Section "{APP_NAME} (required)" SecMain
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    File /r "..\\dist\\{APP_NAME_SHORT}\\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\\{APP_NAME_SHORT}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}" \\
        "DisplayName" "{APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}" \\
        "UninstallString" "$\\"$INSTDIR\\Uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}" \\
        "DisplayIcon" "$\\"$INSTDIR\\{APP_NAME_SHORT}.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}" \\
        "Publisher" "{APP_PUBLISHER}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}" \\
        "DisplayVersion" "{APP_VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}" \\
        "URLInfoAbout" "{APP_URL}"
    
    ; Get installed size
    ${{GetSize}} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}" \\
        "EstimatedSize" "$0"
    
    ; Create runtime directories
    CreateDirectory "$INSTDIR\\data"
    CreateDirectory "$INSTDIR\\logs"
    CreateDirectory "$INSTDIR\\screenshots"
    CreateDirectory "$INSTDIR\\documents"
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\\{APP_NAME}.lnk" "$INSTDIR\\{APP_NAME_SHORT}.exe" "" "$INSTDIR\\{APP_NAME_SHORT}.exe" 0
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\\{APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\{APP_NAME}\\{APP_NAME}.lnk" "$INSTDIR\\{APP_NAME_SHORT}.exe"
    CreateShortCut "$SMPROGRAMS\\{APP_NAME}\\{APP_NAME} Voice Mode.lnk" "$INSTDIR\\{APP_NAME_SHORT}.exe" "--voice-only"
    CreateShortCut "$SMPROGRAMS\\{APP_NAME}\\{APP_NAME} Web Dashboard.lnk" "$INSTDIR\\{APP_NAME_SHORT}.exe" "--web"
    CreateShortCut "$SMPROGRAMS\\{APP_NAME}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Start with Windows" SecAutoStart
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "{APP_NAME_SHORT}" \\
        "$\\"$INSTDIR\\{APP_NAME_SHORT}.exe$\\" --voice-only"
SectionEnd

; ----- Section Descriptions -----
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecMain}} "Install {APP_NAME} core files."
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecDesktop}} "Create a shortcut on the Desktop."
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecStartMenu}} "Create Start Menu shortcuts."
    !insertmacro MUI_DESCRIPTION_TEXT ${{SecAutoStart}} "Launch {APP_NAME} in voice mode when Windows starts."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ----- Uninstaller Section -----
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\\{APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\\{APP_NAME}"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME_SHORT}"
    DeleteRegKey HKLM "Software\\{APP_NAME_SHORT}"
    DeleteRegValue HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "{APP_NAME_SHORT}"
SectionEnd
"""
    return script


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate installer configurations for Jarvis V2"
    )
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux", "all"],
        default="all",
        help="Target platform (default: all)",
    )
    parser.add_argument(
        "--nsis",
        action="store_true",
        help="Generate NSIS script as alternative to Inno Setup",
    )
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Jarvis V2 - Installer Configuration Generator")
    print(f"{'='*60}\n")

    platforms = (
        ["windows", "macos", "linux"]
        if args.platform == "all"
        else [args.platform]
    )

    for platform in platforms:
        print(f"\n--- {platform.upper()} ---")
        if platform == "macos":
            generate_macos_app_bundle()
        elif platform == "linux":
            generate_linux_desktop()
        elif platform == "windows":
            if args.nsis:
                nsis_script = generate_nsis_script()
                nsis_path = HERE / "installer.nsi"
                nsis_path.write_text(nsis_script)
                print(f"[OK] NSIS script written to: {nsis_path}")
                print("     Build with: makensis packaging/installer.nsi")
            else:
                print("[OK] Windows installer uses Inno Setup (packaging/installer.iss)")
                print("     Run: packaging\\BuildInstaller.bat")

    print(f"\n{'='*60}")
    print(f"  Done! See above for build instructions.")
    print(f"{'='*60}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

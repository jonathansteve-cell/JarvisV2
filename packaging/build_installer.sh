#!/usr/bin/env bash
# ================================================================
# Jarvis V2 - Complete Installer Builder (macOS / Linux)
# ================================================================
# This script builds a portable app bundle.
# For a proper .dmg (macOS) or .deb/.AppImage (Linux), see below.
# ================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ============================================================"
echo "   JARVIS V2 - INSTALLER BUILDER"
echo "  ============================================================"
echo "   Builds a portable app bundle for macOS / Linux."
echo "  ============================================================"
echo -e "${NC}"

PY_BIN="${PYTHON:-python3}"
command -v "$PY_BIN" >/dev/null 2>&1 || { echo -e "${RED}[ERROR] $PY_BIN not found${NC}"; exit 1; }

PYVER=$("$PY_BIN" --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[CHECK]${NC} Python $PYVER found."

# ---------------------------------------------------------------
# Step 1: Virtual environment
# ---------------------------------------------------------------
echo ""
echo -e "${CYAN}[1/5] Creating virtual environment...${NC}"
if [ ! -d .venv ]; then
    "$PY_BIN" -m venv .venv
    echo "      Virtual environment created."
else
    echo "      Virtual environment already exists."
fi
source .venv/bin/activate

# ---------------------------------------------------------------
# Step 2: Dependencies
# ---------------------------------------------------------------
echo ""
echo -e "${CYAN}[2/5] Installing dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q
echo "      All dependencies installed."

# Linux: check for tkinter
if [ "$(uname -s)" = "Linux" ] && ! "$PY_BIN" -c 'import tkinter' >/dev/null 2>&1; then
    echo -e "${YELLOW}[WARN]${NC} tkinter is missing. Install it:"
    echo "         sudo apt install python3-tk        # Debian/Ubuntu"
    echo "         sudo dnf install python3-tkinter   # Fedora"
fi

# ---------------------------------------------------------------
# Step 3: Generate icon
# ---------------------------------------------------------------
echo ""
echo -e "${CYAN}[3/5] Generating application icon...${NC}"
"$PY_BIN" packaging/make_icon.py || echo -e "${YELLOW}[WARN]${NC} Icon generation skipped."

# ---------------------------------------------------------------
# Step 4: Build with PyInstaller
# ---------------------------------------------------------------
echo ""
echo -e "${CYAN}[4/5] Building JarvisV2 with PyInstaller...${NC}"
echo "      This may take 2-5 minutes..."
"$PY_BIN" -m PyInstaller --noconfirm --clean packaging/jarvis.spec

# Create runtime directories
mkdir -p dist/JarvisV2/{data,logs,screenshots,documents}

# Copy config files
cp -f config/config.json dist/JarvisV2/config/ 2>/dev/null || true
cp -f config/config.example.json dist/JarvisV2/config/ 2>/dev/null || true

echo -e "${GREEN}      JarvisV2 built successfully!${NC}"

# ---------------------------------------------------------------
# Step 5: Platform-specific packaging
# ---------------------------------------------------------------
echo ""
echo -e "${CYAN}[5/5] Platform-specific packaging...${NC}"

OS="$(uname -s)"
case "$OS" in
    Darwin)
        echo "      macOS detected."
        echo ""
        echo "      To create a .dmg installer, you can use:"
        echo "        brew install create-dmg"
        echo "        create-dmg --volname 'Jarvis V2' --window-pos 200 120 \\"
        echo "          --window-size 600 400 --icon-size 100 --icon 'JarvisV2.app' 175 190 \\"
        echo "          --app-drop-link 425 190 'dist/JarvisV2.dmg' 'dist/JarvisV2/'"
        echo ""
        echo "      For a .app bundle, add a BUNDLE step to packaging/jarvis.spec"
        echo "      or use py2app."
        ;;
    Linux)
        echo "      Linux detected."
        echo ""
        echo "      Portable app is ready at: dist/JarvisV2/"
        echo ""
        echo "      To create an AppImage:"
        echo "        1. Download appimagetool from https://github.com/AppImage/AppImageKit"
        echo "        2. Create JarvisV2.AppDir structure"
        echo "        3. Run: ./appimagetool JarvisV2.AppDir JarvisV2.AppImage"
        echo ""
        echo "      To create a .deb package:"
        echo "        Use: dpkg-deb --build jarvisv2_2.0.0_amd64"
        ;;
    *)
        echo "      Unknown OS: $OS"
        ;;
esac

echo ""
echo -e "${GREEN}  ============================================================${NC}"
echo -e "${GREEN}   BUILD COMPLETE!${NC}"
echo -e "${GREEN}  ============================================================${NC}"
echo ""
echo "   Portable app:  dist/JarvisV2/JarvisV2"
echo ""
echo "   To run:"
echo "     cd dist/JarvisV2 && ./JarvisV2"
echo ""
echo -e "${GREEN}  ============================================================${NC}"

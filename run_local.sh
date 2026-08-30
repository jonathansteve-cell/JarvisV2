#!/usr/bin/env bash
# Jarvis V2 - Voice AI Assistant (Linux/macOS)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ============================================================"
echo "   JARVIS V2 - VOICE AI ASSISTANT"
echo "  ============================================================"
echo "   Starting Voice-Only 3D Interface..."
echo "  ============================================================"
echo -e "${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[ERROR] Python not found!${NC}"
    echo ""
    echo "  Please install Python 3.10+ from:"
    echo "    https://python.org"
    echo ""
    exit 1
fi

PYVER=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[CHECK]${NC} Python $PYVER found."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${CYAN}[INFO]${NC} First run detected. Setting up environment..."
    echo ""
    
    # Create virtual environment
    echo "  [1/4] Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    
    # Activate
    source .venv/bin/activate
    
    # Install dependencies
    echo "  [2/4] Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    
    # Setup configuration
    echo "  [3/4] Setting up configuration..."
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        cp .env.example .env
        echo "        Created .env from template"
    fi
    
    # Create runtime folders
    echo "  [4/4] Creating runtime folders..."
    mkdir -p data logs screenshots documents research
    
    echo ""
    echo -e "${GREEN}  Setup complete!${NC}"
    echo ""
else
    # Activate existing virtual environment
    source .venv/bin/activate
fi

# Check for tkinter
if ! $PYTHON_CMD -c 'import tkinter' 2>/dev/null; then
    echo -e "${RED}[ERROR]${NC} tkinter is missing. Install it:"
    echo "         sudo apt install python3-tk        # Debian/Ubuntu"
    echo "         sudo dnf install python3-tkinter   # Fedora"
    echo "         brew install python-tk@3.11        # macOS"
    echo ""
    exit 1
fi

# Launch Voice-Only 3D UI
echo -e "${CYAN}  Launching Jarvis V2 Voice AI...${NC}"
echo ""

$PYTHON_CMD launch_voice_ui.py

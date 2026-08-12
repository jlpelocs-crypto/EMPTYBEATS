#!/usr/bin/env bash
# EMPTYBEATS COPYRIGHT MARKER: 45524D5054594245415453
# COPYRIGHT TOKEN (base64): RU1QVFRCWUJFQVRTLUNPUlBPSUdIVA==
# Copyright (c) 2026 EMPTYBEATS
# Licensed under the EMPTYBEATS Custom License. See LICENSE.

# Gaming Hub Installer for Linux
# Installs dependencies, creates virtual environment, and sets up desktop shortcuts

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="Gaming Hub"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python"
DESKTOP_ENTRY="$HOME/.local/share/applications/gaming-hub.desktop"
DESKTOP_SHORTCUT="$HOME/Desktop/Gaming Hub.desktop"
ICON_PATH="$SCRIPT_DIR/gaming-hub-icon.svg"

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}   Gaming Hub - Linux Installer${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# Check if Python 3 is installed
echo -e "${YELLOW}[1/5] Checking Python 3 installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3 first:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv python3-tk"
    echo "  Fedora: sudo dnf install python3 python3-tkinter"
    echo "  Arch: sudo pacman -S python tk"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 is installed${NC}"
echo

# Create virtual environment if it doesn't exist
echo -e "${YELLOW}[2/5] Setting up virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    if ! python3 -m venv "$VENV_DIR"; then
        echo -e "${RED}✗ Failed to create virtual environment${NC}"
        echo "Try installing python3-venv:"
        echo "  Ubuntu/Debian: sudo apt install python3-venv"
        echo "  Fedora: sudo dnf install python3-venv"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Virtual environment ready${NC}"
echo

# Upgrade pip and install requirements
echo -e "${YELLOW}[3/5] Installing Python dependencies...${NC}"
"$PYTHON_BIN" -m pip install --upgrade pip > /dev/null 2>&1
"$PYTHON_BIN" -m pip install -r "$SCRIPT_DIR/requirements.txt"
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo

# Ensure scrcpy is installed and recent enough for audio flag support
echo -e "${YELLOW}[3.5/5] Checking scrcpy installation...${NC}"
if command -v scrcpy >/dev/null 2>&1; then
    echo -e "${GREEN}✓ scrcpy found in PATH${NC}"
else
    echo -e "${YELLOW}scrcpy not found. Attempting to install...${NC}"
    if command -v apt-get >/dev/null 2>&1; then
        echo "Installing scrcpy via apt-get (requires sudo)..."
        sudo apt-get update && sudo apt-get install -y scrcpy || true
    elif command -v snap >/dev/null 2>&1; then
        echo "Installing scrcpy via snap (may require sudo)..."
        sudo snap install scrcpy || true
    elif command -v dnf >/dev/null 2>&1; then
        echo "Installing scrcpy via dnf (requires sudo)..."
        sudo dnf install -y scrcpy || true
    else
        echo -e "${YELLOW}Could not automatically install scrcpy. Please install scrcpy manually.${NC}"
    fi
fi
echo

# Create desktop entry
echo -e "${YELLOW}[4/5] Creating desktop application entry...${NC}"
mkdir -p "$HOME/.local/share/applications"

# Create the .desktop file
cat > "$DESKTOP_ENTRY" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Gaming Hub
Comment=Optimize and mirror Huawei MatePad SE
Exec=sh -c 'cd "INSTALL_DIR" && ./run_gaming_hub.sh'
Icon=ICON_PATH
Categories=Utility;System;
Terminal=false
StartupNotify=true
EOF

# Replace INSTALL_DIR placeholder with actual path
sed -i "s|INSTALL_DIR|$SCRIPT_DIR|g" "$DESKTOP_ENTRY"
# Replace ICON_PATH placeholder with actual icon path
sed -i "s|ICON_PATH|$ICON_PATH|g" "$DESKTOP_ENTRY"

chmod +x "$DESKTOP_ENTRY"
echo -e "${GREEN}✓ Desktop entry created at $DESKTOP_ENTRY${NC}"
echo

# Create desktop shortcut if Desktop directory exists
echo -e "${YELLOW}[5/5] Creating desktop shortcut...${NC}"
if [ -d "$HOME/Desktop" ]; then
    cp "$DESKTOP_ENTRY" "$DESKTOP_SHORTCUT"
    chmod +x "$DESKTOP_SHORTCUT"
    echo -e "${GREEN}✓ Desktop shortcut created${NC}"
else
    echo -e "${YELLOW}⚠ Desktop folder not found, skipping shortcut${NC}"
fi
echo

# Summary
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${BLUE}===============================================${NC}"
echo
echo "You can now run Gaming Hub in several ways:"
echo
echo "  1. From command line:"
echo "     cd \"$SCRIPT_DIR\" && ./run_gaming_hub.sh"
echo
echo "  2. From application menu (search for 'Gaming Hub')"
echo
if [ -f "$DESKTOP_SHORTCUT" ]; then
    echo "  3. Double-click the Gaming Hub icon on your Desktop"
    echo
fi
echo -e "${YELLOW}Note: First launch may take a moment as Python packages are loaded.${NC}"
echo

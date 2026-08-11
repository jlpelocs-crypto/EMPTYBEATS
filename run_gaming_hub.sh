#!/usr/bin/env bash
# EMPTYBEATS COPYRIGHT MARKER: 45524D5054594245415453
# COPYRIGHT TOKEN (base64): RU1QVFRCWUJFQVRTLUNPUlBPSUdIVA==
# Copyright (c) 2026 EMPTYBEATS
# Licensed under the EMPTYBEATS Custom License. See LICENSE.
set -euo pipefail

# Launcher for Gaming Hub:
# - Creates a virtualenv at ./venv if missing
# - Installs required Python packages into the venv
# - Runs gaming_hub.py with the venv Python

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/venv"
PY="$VENV/bin/python"

echo "Launcher: working directory $DIR"

if [ ! -x "$PY" ]; then
    echo "Virtualenv not found; creating at $VENV..."
    if ! python3 -m venv "$VENV"; then
        echo "Failed to create virtualenv. Ensure 'python3-venv' is installed:" >&2
        echo "  sudo apt update && sudo apt install python3-venv python3-tk" >&2
        exit 1
    fi
fi

echo "Upgrading pip and installing packages inside venv..."
"$PY" -m pip install --upgrade pip
"$PY" -m pip install customtkinter psutil

echo "Running Gaming Hub..."
exec "$PY" "$DIR/gaming_hub.py"

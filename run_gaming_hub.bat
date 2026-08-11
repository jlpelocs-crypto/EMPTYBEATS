@echo off
REM EMPTYBEATS COPYRIGHT MARKER: 45524D5054594245415453
REM COPYRIGHT TOKEN (base64): RU1QVFRCWUJFQVRTLUNPUlBPSUdIVA==
REM Copyright (c) 2026 EMPTYBEATS
REM Licensed under the EMPTYBEATS Custom License. See LICENSE.
setlocal
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found in PATH.
    echo Install Python 3 and try again.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv "%SCRIPT_DIR%venv"
)

call "%SCRIPT_DIR%venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul
python -m pip install customtkinter psutil >nul
python "%SCRIPT_DIR%gaming_hub.py"

@echo off
REM EMPTYBEATS COPYRIGHT MARKER: 45524D5054594245415453
REM COPYRIGHT TOKEN (base64): RU1QVFRCWUJFQVRTLUNPUlBPSUdIVA==
REM Copyright (c) 2026 EMPTYBEATS
REM Licensed under the EMPTYBEATS Custom License. See LICENSE.

REM Gaming Hub Installer for Windows
REM Installs dependencies, creates virtual environment, and sets up desktop shortcuts

setlocal enabledelayedexpansion

cls
echo ===============================================
echo    Gaming Hub - Windows Installer
echo ===============================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "APP_NAME=Gaming Hub"
set "ICON_PATH=%SCRIPT_DIR%gaming-hub-icon.ico"

REM Check if Python is installed
echo [1/5] Checking Python installation...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python 3 is not found in PATH
    echo.
    echo Please install Python 3 from: https://www.python.org/downloads/
    echo During installation, make sure to CHECK "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo [OK] Python is installed
echo.

REM Create virtual environment if it doesn't exist
echo [2/5] Setting up virtual environment...
if not exist "%PYTHON_EXE%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)
echo [OK] Virtual environment ready
echo.

REM Upgrade pip and install requirements
echo [3/5] Installing Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create desktop shortcut using PowerShell
echo [4/5] Creating desktop shortcut...

set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_PATH=%DESKTOP%\Gaming Hub.lnk"
set "SCRIPT_PATH=%SCRIPT_DIR%run_gaming_hub.bat"

powershell -nologo -noprofile -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); " ^
    "$Shortcut.TargetPath = '%SCRIPT_PATH%'; " ^
    "$Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; " ^
    "$Shortcut.Description = '%APP_NAME%'; " ^
    "$icon = '%ICON_PATH%'; if (Test-Path $icon) { $Shortcut.IconLocation = $icon } else { $Shortcut.IconLocation = 'C:\\Windows\\System32\\shell32.dll, 12' }; " ^
    "$Shortcut.Save()" >nul 2>&1

if errorlevel 1 (
    echo [WARNING] Could not create desktop shortcut automatically
) else (
    echo [OK] Desktop shortcut created
)
echo.

REM Create Start Menu shortcut
echo [5/5] Creating Start Menu entry...

set "APPDATA_START=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "START_SHORTCUT=%APPDATA_START%\Gaming Hub.lnk"

if not exist "%APPDATA_START%" mkdir "%APPDATA_START%"

powershell -nologo -noprofile -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%START_SHORTCUT%'); " ^
    "$Shortcut.TargetPath = '%SCRIPT_PATH%'; " ^
    "$Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; " ^
    "$Shortcut.Description = '%APP_NAME%'; " ^
    "$icon = '%ICON_PATH%'; if (Test-Path $icon) { $Shortcut.IconLocation = $icon } else { $Shortcut.IconLocation = 'C:\\Windows\\System32\\shell32.dll, 12' }; " ^
    "$Shortcut.Save()" >nul 2>&1

if errorlevel 1 (
    echo [WARNING] Could not create Start Menu shortcut
) else (
    echo [OK] Start Menu entry created
)
echo.

REM Summary
cls
echo ===============================================
echo    Installation Complete!
echo ===============================================
echo.
echo You can now run Gaming Hub in several ways:
echo.
echo  1. Double-click "Gaming Hub" shortcut on your Desktop
echo.
echo  2. Search for "Gaming Hub" in Windows Start Menu
echo.
echo  3. From command line:
echo     cd "%SCRIPT_DIR%" ^&^& run_gaming_hub.bat
echo.
echo  4. Run this installer again anytime to update dependencies
echo.
echo Note: First launch may take a moment as Python packages are loaded.
echo.
pause

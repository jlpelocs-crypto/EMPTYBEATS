# Gaming Hub - Installation Guide

## Quick Start

### For Linux Users 🐧

1. **Open Terminal** in the Gaming Hub directory
2. **Run the installer:**
   ```bash
   chmod +x install_linux.sh
   ./install_linux.sh
   ```
3. **Wait for completion** - The installer will:
   - Check Python 3 installation
   - Create a virtual environment
   - Install all Python dependencies
   - Create a desktop application entry
   - Create a desktop shortcut (if Desktop exists)

4. **Launch the app:**
   - Double-click "Gaming Hub" on your Desktop, OR
   - Search for "Gaming Hub" in your applications menu, OR
   - Run: `cd /path/to/gaming_hub && ./run_gaming_hub.sh`

---

### For Windows Users 🪟

1. **Right-click** `install_windows.bat`
2. **Select "Run as Administrator"**
3. **Wait for completion** - The installer will:
   - Check Python 3 installation
   - Create a virtual environment
   - Install all Python dependencies
   - Create a desktop shortcut
   - Create a Start Menu entry

4. **Launch the app:**
   - Double-click "Gaming Hub" shortcut on Desktop, OR
   - Search for "Gaming Hub" in Windows Start Menu, OR
   - Double-click `run_gaming_hub.bat`

---

## Pre-Requirements

### Linux
- **Python 3** (required)
- **python3-venv** (for virtual environment)
- **python3-tk** (for Tkinter support)

**Auto-Install via installer** ✓

If the installer fails, manually install:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-venv python3-tk

# Fedora
sudo dnf install python3 python3-venv python3-tkinter

# Arch
sudo pacman -S python tk
```

### Windows
- **Python 3.8+** (required)
  - Download from: https://www.python.org/downloads/
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

**Auto-Install via installer** ✓

---

## Troubleshooting

### Linux Issues

**"Permission denied" error:**
```bash
chmod +x install_linux.sh
./install_linux.sh
```

**"python3 not found":**
```bash
sudo apt install python3
```

**"venv module not available":**
```bash
sudo apt install python3-venv
```

### Windows Issues

**"Python was not found in PATH":**
1. Uninstall Python completely
2. Download from https://www.python.org/downloads/
3. Run the installer
4. ⚠️ Check "Add Python to PATH" during installation
5. Restart your computer
6. Run the Gaming Hub installer again

**"Permission denied" on Windows:**
- Right-click `install_windows.bat`
- Select "Run as Administrator"

**Desktop shortcut not created:**
- Manually run: `cd path\to\gaming_hub && run_gaming_hub.bat`
- Or create a shortcut manually pointing to `run_gaming_hub.bat`

---

## Manual Installation (If Needed)

### Linux
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 gaming_hub.py
```

### Windows
```cmd
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run the app
python gaming_hub.py
```

---

## What Gets Installed

**Python Packages:**
- `customtkinter` - Modern GUI framework
- `psutil` - System monitoring utilities

**System Binaries (Separate Installation):**
- `adb` (Android Debug Bridge) - For device communication
- `scrcpy` - For screen mirroring

---

## After Installation

You can safely:
- **Delete the installer files** (they're only needed for initial setup)
- **Keep the `venv/` folder** (contains all dependencies)
- **Share the folder** with others - they just need to run the installer

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Ensure Python is properly installed
3. Try running the installer again
4. Check error messages in the terminal window

---

**Happy gaming!** 🎮

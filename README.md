Gaming Hub
===========

About
-----

Gaming Hub is a lightweight desktop utility for optimizing Android tablet performance and mirroring device screens using `adb` and `scrcpy`. It provides simple controls for boosting device settings, recording gameplay locally or on-device, and managing low-end laptop workflows on Linux and Windows.

Setup
-----

1. Install system Tk (needed by tkinter):

```bash
sudo apt update
sudo apt install -y python3-tk python3-pip
```

2. Install Python dependencies (per-user):

```bash
python3 -m pip install --user -r ~/Downloads/optimize/requirements.txt
export PATH="$HOME/.local/bin:$PATH"
```

Or use a virtualenv:

```bash
python3 -m venv ~/gaming_hub_venv
source ~/gaming_hub_venv/bin/activate
pip install -r ~/Downloads/optimize/requirements.txt
```

3. Ensure `adb` and `scrcpy` are installed:

```bash
sudo apt install android-tools-adb scrcpy
# or: sudo snap install scrcpy
```

Run
---

```bash
python3 ~/Downloads/optimize/gaming_hub.py
```

Or on Windows:

```bat
run_gaming_hub.bat
```

Notes
-----
- The GUI polls system RAM/CPU and checks for connected ADB devices.
- Android phones/tablets are supported directly with `adb` and `scrcpy` on both Linux and Windows.
- iOS is not mirrored natively on Linux or Windows by this app; it shows a helpful note and points users to an external workflow such as AirPlay/OBS on a Mac or Windows host.
- If `customtkinter` is missing, install it into the same Python interpreter used to run the app.
- Log output is shown inside the app. Use the Stop button to terminate scrcpy processes safely.

License
-------

This project is licensed under the EMPTYBEATS Custom License. See `LICENSE` for details.

Optimized Mirror/Content Workflow
---------------------------------
- Use `Start Mirror` with your chosen resolution (1280/720/480) and bitrate (4M/6M/8M/12M).
- `Record (Host)` captures directly through `scrcpy` to your laptop.
- `Device-side Recording` uses `adb shell screenrecord` on the phone and then pulls the final file to your machine.
- Use `Use device recording by default` when you want every Record action to prefer device-side capture.
- For smoother content: prefer 720p or 480p at 8M if your laptop is low on RAM, and use device-side recording for the least host overhead.
- Use the `Low-End Laptop Mode` button for a one-click preset that switches to 480p, 4M bitrate, device recording, and 30fps for a lighter experience on older or low-RAM machines.
- On Linux laptops, use the `Enable ZRAM (Linux only)` button to add a compressed RAM swap layer that can improve smoothness on low-RAM systems. This is especially helpful for 4GB/6GB laptops. On Windows, the app will show a notice that ZRAM is not available.
- On Windows, install Python, `customtkinter`, `psutil`, `adb`, and `scrcpy` first, then run `run_gaming_hub.bat`.

Recording & Performance Tips
---------------------------
- New UI options: select `Bitrate` (4M/6M/8M/12M) and `Resolution` (1280/720/480).
- Use the `Record (Host)` button to capture through `scrcpy` on the laptop.
- Use `Device-side Recording` to run `adb shell screenrecord` on the tablet and automatically pull the file when it finishes.
- Enable `Use device recording by default` to make the Record button use device-side recording automatically.
- If you experience lag during fast gameplay, try:
  - Increasing bitrate (8M or 12M) if USB bandwidth allows.
  - Lowering resolution (720 or 480).
  - Using device-side recording to offload encoding to the tablet.
  - Connecting through a USB 3 port and closing background apps on both devices.

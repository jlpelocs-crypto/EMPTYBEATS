#!/usr/bin/env python3
# EMPTYBEATS COPYRIGHT MARKER: 45524D5054594245415453
# COPYRIGHT TOKEN (base64): RU1QVFRCWUJFQVRTLUNPUlBPSUdIVA==
# Copyright (c) 2026 EMPTYBEATS
# Licensed under the EMPTYBEATS Custom License. See LICENSE.
"""
Gaming Hub — CustomTkinter GUI for optimizing and mirroring Huawei MatePad SE

Requirements:
 - Python3 on Linux
 - customtkinter, psutil
 - adb (Android platform-tools), scrcpy installed (scrcpy snap in /snap/bin)

Save as `gaming_hub.py` and run: `python3 gaming_hub.py`
"""
import os
import sys
import threading
import subprocess
import shlex
import signal
import time
import platform
import shutil
from datetime import datetime

# Auto-install missing Python dependencies if needed.
_missing_python_packages = []
try:
    import customtkinter as ctk
except ImportError:
    _missing_python_packages.append("customtkinter")

try:
    import psutil
except ImportError:
    _missing_python_packages.append("psutil")

if _missing_python_packages:
    try:
        print("Installing missing Python packages:", " ".join(_missing_python_packages))
        subprocess.check_call([sys.executable, "-m", "pip", "install", *[_missing_python_packages]])
    except Exception as e:
        print("Failed to automatically install Python dependencies:", e)
        raise

    import customtkinter as ctk
    import psutil

from tkinter import messagebox


class ProcessWrapper:
    def __init__(self, popen: subprocess.Popen, title: str):
        self.popen = popen
        self.title = title

    def is_running(self):
        return self.popen and (self.popen.poll() is None)

    def terminate(self):
        try:
            if self.is_running():
                if sys.platform.startswith("win"):
                    self.popen.terminate()
                else:
                    os.killpg(os.getpgid(self.popen.pid), signal.SIGTERM)
                self.popen.wait(timeout=5)
        except Exception:
            try:
                self.popen.terminate()
            except Exception:
                pass


class GamingHubApp:
    def __init__(self, root):
        self.platform = platform.system().lower()
        self.is_windows = self.platform == "windows"
        self.is_linux = self.platform == "linux"
        self.root = root
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.title("Gaming Hub — Android & iOS Device Mirror")
        self.root.geometry("950x620")

        self.proc: ProcessWrapper | None = None
        self.monitoring = True

        self._build_ui()

        # Start background monitor thread
        self.monitor_thread = threading.Thread(target=self._hardware_monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Schedule periodic UI updates
        self._update_ui_loop()

        # Bind close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Main frame
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Top status cards
        self.cards_frame = ctk.CTkFrame(self.frame)
        self.cards_frame.pack(fill="x", padx=6, pady=6)

        self.ram_card = self._make_card(self.cards_frame, "RAM Usage", "—")
        self.zram_card = self._make_card(self.cards_frame, "ZRAM Status", "—")
        self.adb_card = self._make_card(self.cards_frame, "ADB Devices", "—")

        self.ram_card.pack(side="left", expand=True, fill="x", padx=6)
        self.zram_card.pack(side="left", expand=True, fill="x", padx=6)
        self.adb_card.pack(side="left", expand=True, fill="x", padx=6)

        # Middle area: logs / info
        self.log_box = ctk.CTkTextbox(self.frame, height=200)
        self.log_box.pack(fill="both", expand=True, padx=6, pady=6)
        self.log_box.insert("0.0", "Gaming Hub started.\n")
        self.log_box.configure(state="disabled")

        # Bottom controls
        controls = ctk.CTkFrame(self.frame)
        controls.pack(fill="x", padx=6, pady=6)

        self.boost_btn = ctk.CTkButton(controls, text="Boost & Optimize Tablet", command=self._on_boost)
        self.mirror_btn = ctk.CTkButton(controls, text="Start Mirror", command=self._on_mirror)
        self.record_btn = ctk.CTkButton(controls, text="Record (Host)", command=self._on_record)
        self.device_record_btn = ctk.CTkButton(controls, text="Device-side Recording", command=self._on_device_record)
        self.live_btn = ctk.CTkButton(controls, text="Live Stream Ready Mode", command=self._on_live)
        self.zram_btn = ctk.CTkButton(controls, text="Enable ZRAM (Linux only)", command=self._on_zram_toggle)
        self.low_end_btn = ctk.CTkButton(controls, text="Low-End Laptop Mode", command=self._apply_low_end_preset)
        self.stop_btn = ctk.CTkButton(controls, text="Stop Process", fg_color="#b22222", hover_color="#ff4444", command=self._on_stop)

        self.boost_btn.pack(side="left", padx=6, pady=6, ipadx=8)
        self.mirror_btn.pack(side="left", padx=6, pady=6, ipadx=8)
        self.record_btn.pack(side="left", padx=6, pady=6, ipadx=8)
        self.device_record_btn.pack(side="left", padx=6, pady=6, ipadx=8)
        self.live_btn.pack(side="left", padx=6, pady=6, ipadx=8)
        self.zram_btn.pack(side="left", padx=6, pady=6, ipadx=8)
        self.low_end_btn.pack(side="left", padx=6, pady=6, ipadx=8)
        self.stop_btn.pack(side="right", padx=6, pady=6, ipadx=8)

        self.zram_notice = ctk.CTkLabel(
            controls,
            text="Linux only • requires sudo • no effect on Windows",
            text_color="#9fb3c8",
            font=ctk.CTkFont(size=11)
        )
        self.zram_notice.pack(side="left", padx=(0, 6), pady=6)

        self.preset_notice = ctk.CTkLabel(
            controls,
            text="Low-end preset: 480p, 4M, device recording, 30fps",
            text_color="#9fb3c8",
            font=ctk.CTkFont(size=11)
        )
        self.preset_notice.pack(side="left", padx=(0, 6), pady=6)

        self.options_frame = ctk.CTkFrame(self.frame)
        self.options_frame.pack(fill="x", padx=6, pady=(0,6))

        self.device_mode = ctk.StringVar(value="Android")
        self.bitrate_values = ["4M", "6M", "8M", "12M"]
        self.resolution_values = ["1280", "720", "480"]
        self.selected_bitrate = ctk.StringVar(value="8M")
        self.selected_resolution = ctk.StringVar(value="1280")
        self.use_device_by_default = ctk.BooleanVar(value=False)

        self.device_mode_menu = ctk.CTkOptionMenu(self.options_frame, values=["Android", "iOS"], variable=self.device_mode)
        self.bitrate_menu = ctk.CTkOptionMenu(self.options_frame, values=self.bitrate_values, variable=self.selected_bitrate)
        self.resolution_menu = ctk.CTkOptionMenu(self.options_frame, values=self.resolution_values, variable=self.selected_resolution)
        self.device_default_switch = ctk.CTkSwitch(self.options_frame, text="Use device recording by default", variable=self.use_device_by_default)

        ctk.CTkLabel(self.options_frame, text="Device:").pack(side="left", padx=(6,2))
        self.device_mode_menu.pack(side="left", padx=(0,12))
        ctk.CTkLabel(self.options_frame, text="Bitrate:").pack(side="left", padx=(6,2))
        self.bitrate_menu.pack(side="left", padx=(0,12))
        ctk.CTkLabel(self.options_frame, text="Resolution:").pack(side="left", padx=(6,2))
        self.resolution_menu.pack(side="left", padx=(0,12))
        self.device_default_switch.pack(side="left", padx=12)

        # Internal state
        self._ram_percent = 0.0
        self._cpu_percent = 0.0
        self._zram_summary = "Unknown"
        self._adb_devices = []
        self._device_record_device_path = None
        self._device_record_local_path = None
        self._low_end_mode = False

    def _make_card(self, parent, title, value_text):
        card = ctk.CTkFrame(parent, height=90)
        title_lbl = ctk.CTkLabel(card, text=title, anchor="w", font=ctk.CTkFont(size=14, weight="bold"))
        value_lbl = ctk.CTkLabel(card, text=value_text, anchor="w", font=ctk.CTkFont(size=18))
        title_lbl.pack(anchor="w", padx=12, pady=(8, 0))
        value_lbl.pack(anchor="w", padx=12, pady=(2, 8))
        card.value_lbl = value_lbl
        return card

    def _hardware_monitor_loop(self):
        # Background loop to poll hardware stats without blocking UI
        while self.monitoring:
            try:
                vm = psutil.virtual_memory()
                self._ram_percent = vm.percent
                # cpu_percent with interval blocks this thread only
                self._cpu_percent = psutil.cpu_percent(interval=1)

                self._zram_summary = self._get_zram_status()
                self._adb_devices = self._get_adb_devices()

            except Exception as e:
                self._log(f"Monitor error: {e}")
            # sleep short, cpu_percent already spent ~1s
            time.sleep(0.5)

    def _update_ui_loop(self):
        # Update cards
        try:
            self.ram_card.value_lbl.configure(text=f"RAM: {self._ram_percent:.0f}% | CPU: {self._cpu_percent:.0f}%")
            self.zram_card.value_lbl.configure(text=self._zram_summary)
            adb_text = f"{len(self._adb_devices)} device(s)"
            if self._adb_devices:
                adb_text += f": {', '.join(self._adb_devices)}"
            self.adb_card.value_lbl.configure(text=adb_text)
        except Exception:
            pass

        # schedule next update
        self.root.after(1500, self._update_ui_loop)

    def _log(self, text: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_log(f"[{timestamp}] {text}\n")

    def _append_log(self, text: str):
        try:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", text)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except Exception:
            pass

    def _get_adb_devices(self):
        try:
            adb_cmd = "adb.exe" if self.is_windows else "adb"
            out = subprocess.check_output([adb_cmd, "devices"], stderr=subprocess.DEVNULL, text=True)
            lines = [l.strip() for l in out.splitlines()]
            devices = []
            for l in lines[1:]:
                if not l:
                    continue
                parts = l.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
        except FileNotFoundError:
            return []
        except Exception:
            return []

    def _run_zramctl(self) -> str:
        try:
            result = subprocess.run(
                ["zramctl"],
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            return output or "zramctl returned empty output."
        except FileNotFoundError:
            return "zramctl not installed or not available in PATH."
        except subprocess.CalledProcessError as exc:
            msg = exc.stderr.strip() or exc.stdout.strip()
            return f"zramctl error: {msg or f'exited with {exc.returncode}'}"
        except Exception as exc:
            return f"ZRAM status check failed: {exc}"

    def _get_zram_status(self):
        if self.is_windows:
            return "ZRAM not available on Windows"
        return self._run_zramctl()

    def _enable_zram_configuration(self) -> str:
        script = r'''
set -e

if ! command -v apt-get >/dev/null 2>&1; then
    echo "This script requires apt-get (Ubuntu/Mint)."
    exit 1
fi

if ! dpkg -s zram-config >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y zram-config
fi

if [ ! -f /usr/bin/init-zram-swapping ]; then
    echo "/usr/bin/init-zram-swapping not found"
    exit 1
fi

mem_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
if [ -z "$mem_kb" ]; then
    echo "Unable to detect total RAM."
    exit 1
fi

if grep -q '^MEMORY_SIZE=' /usr/bin/init-zram-swapping; then
    sed -i "s|^MEMORY_SIZE=.*|MEMORY_SIZE=${mem_kb}K|" /usr/bin/init-zram-swapping
else
    printf 'MEMORY_SIZE=%sK\n' "${mem_kb}" >> /usr/bin/init-zram-swapping
fi

if grep -q '^COMPRESSION_ALGO=' /usr/bin/init-zram-swapping; then
    sed -i 's|^COMPRESSION_ALGO=.*|COMPRESSION_ALGO=zstd|' /usr/bin/init-zram-swapping
else
    printf 'COMPRESSION_ALGO=zstd\n' >> /usr/bin/init-zram-swapping
fi

systemctl restart zram-config.service
echo "ZRAM configured for 100% RAM and zstd compression."
'''
        executor = "pkexec" if shutil.which("pkexec") else "sudo"
        try:
            result = subprocess.run(
                [executor, "bash", "-lc", script],
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            if result.stderr.strip():
                output += "\n" + result.stderr.strip()
            return output.strip() or "ZRAM enable command completed successfully."
        except FileNotFoundError:
            return "Neither pkexec nor sudo was found on this system."
        except subprocess.CalledProcessError as exc:
            stdout = exc.stdout.strip()
            stderr = exc.stderr.strip()
            message = "Failed to enable ZRAM."
            if stdout:
                message += f"\n{stdout}"
            if stderr:
                message += f"\n{stderr}"
            return message.strip()
        except Exception as exc:
            return f"Unable to run ZRAM enable command: {exc}"

    def _enable_zram_task(self):
        self._log("Starting ZRAM enable sequence...")
        result = self._enable_zram_configuration()
        self._log(result)
        try:
            messagebox.showinfo("ZRAM", result)
        except Exception:
            pass
        self._zram_summary = self._run_zramctl()

    def _ensure_android_device(self):
        if self.device_mode.get() == "iOS":
            messagebox.showinfo("iOS support", "iOS mirroring on Linux is limited and usually requires a separate AirPlay/OBS workflow or a Mac/Windows-based tool. This app currently supports Android devices directly.")
            return False
        devices = self._get_adb_devices()
        if not devices:
            messagebox.showerror("ADB Device", "No Android device found. Please enable USB debugging and connect the phone/tablet.")
            return False
        return True

    def _on_zram_toggle(self):
        if self.is_windows:
            messagebox.showinfo("ZRAM", "ZRAM is a Linux feature and is not available on Windows.")
            return
        thread = threading.Thread(target=self._enable_zram_task, daemon=True)
        thread.start()

    def _on_boost(self):
        # Run ADB optimization sequence in background
        if not self._ensure_android_device():
            return

        t = threading.Thread(target=self._adb_optimize_sequence, daemon=True)
        t.start()

    def _adb_optimize_sequence(self):
        self._log("Starting ADB optimize sequence...")
        commands = [
            "settings put global power_mode 1",
            "settings put global low_power 0",
            "settings put global thermal_limit_balancing 0",
            "settings put global touch_pump_rate 1",
            "settings put global show_background_blur 0",
        ]

        for cmd in commands:
            full = f"adb shell {cmd}"
            self._log(f"Running: {cmd}")
            try:
                res = subprocess.run(shlex.split(full), capture_output=True, text=True, timeout=15)
                if res.returncode != 0:
                    self._log(f"Command failed: {res.stderr.strip()}")
            except Exception as e:
                self._log(f"ADB error: {e}")

        self._log("ADB optimize sequence complete.")

    def _get_adb_executable(self):
        return "adb.exe" if self.is_windows else "adb"

    def _get_scarpy_executable(self):
        if self.is_windows:
            return "scrcpy.exe"
        return "/snap/bin/scrcpy"

    def _get_selected_bitrate(self):
        try:
            return self.selected_bitrate.get()
        except Exception:
            return "8M"

    def _get_selected_resolution(self):
        try:
            return self.selected_resolution.get()
        except Exception:
            return "1280"

    def _get_selected_fps(self):
        return 30 if self._low_end_mode else 60

    def _apply_low_end_preset(self):
        self.selected_bitrate.set("4M")
        self.selected_resolution.set("480")
        self.use_device_by_default.set(True)
        self._low_end_mode = True
        self._log("Applied low-end laptop preset: 480p, 4M, device recording, 30fps")
        messagebox.showinfo("Low-End Laptop Mode", "Applied a smoother preset for lower-end laptops: 480p, 4M bitrate, device recording, and 30fps.")

    def _on_mirror(self):
        if not self._ensure_android_device():
            return
        resolution = self._get_selected_resolution()
        bitrate = self._get_selected_bitrate()
        fps = self._get_selected_fps()
        args = [self._get_scarpy_executable(), "-m", resolution, "-b", bitrate, f"--max-fps={fps}", "--no-audio"]
        self._start_process(args, title="scrcpy-mirror")

    def _on_record(self):
        if not self._ensure_android_device():
            return
        if self.use_device_by_default.get():
            self._on_device_record()
            return
        home = os.path.expanduser("~")
        fname = datetime.now().strftime("hok_huawei_%Y%m%d_%H%M%S.mp4")
        fullpath = os.path.join(home, fname)
        resolution = self._get_selected_resolution()
        bitrate = self._get_selected_bitrate()
        fps = self._get_selected_fps()
        args = [self._get_scarpy_executable(), "-m", resolution, "-b", bitrate, f"--max-fps={fps}", "--no-audio", "--record", fullpath]
        self._start_process(args, title="scrcpy-record")
        self._log(f"Recording will be saved to: {fullpath}")

    def _on_device_record(self):
        if not self._ensure_android_device():
            return
        fname = datetime.now().strftime("hok_huawei_device_%Y%m%d_%H%M%S.mp4")
        device_path = f"/sdcard/{fname}"
        home = os.path.expanduser("~")
        local_path = os.path.join(home, fname)
        self._device_record_device_path = device_path
        self._device_record_local_path = local_path

        resolution = self._get_selected_resolution()
        try:
            bitrate_num = int(self._get_selected_bitrate().rstrip("M")) * 1000000
        except Exception:
            bitrate_num = 8000000

        try:
            w = int(resolution)
            h = int(w * 9 / 16)
            size_arg = f"{w}x{h}"
        except Exception:
            size_arg = f"{resolution}x720"

        adb_cmd = "adb.exe" if self.is_windows else "adb"
        args = [adb_cmd, "shell", "screenrecord", "--size", size_arg, "--bit-rate", str(bitrate_num), device_path]
        self._log(f"Starting device recording -> {device_path} (size {size_arg}, bitrate {bitrate_num})")
        self._start_process(args, title="device-record")

    def _on_live(self):
        if not self._ensure_android_device():
            return
        resolution = self._get_selected_resolution()
        bitrate = self._get_selected_bitrate()
        fps = self._get_selected_fps()
        args = [
            self._get_scarpy_executable(),
            "-m", resolution,
            "-b", bitrate,
            f"--max-fps={fps}",
            "--no-audio",
            "--always-on-top",
            "--window-borderless",
            "--render-expired-frames",
            "--stay-awake",
            "--window-title", "Device Mirror - OBS",
            "--window-width", resolution,
            "--window-height", str(int(int(resolution) * 9 / 16)),
        ]
        self._start_process(args, title="scrcpy-live")

    def _start_process(self, cmd, title: str):
        if self.proc and self.proc.is_running():
            messagebox.showinfo("Process Running", "A mirroring process is already running. Stop it first.")
            return

        self._log(f"Starting: {cmd}")
        try:
            if isinstance(cmd, str):
                args = shlex.split(cmd)
            else:
                args = cmd
            if self.is_windows:
                popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
            self.proc = ProcessWrapper(popen, title)

            # Spin threads to read stdout and stderr
            stdout_thread = threading.Thread(target=self._read_stream, args=(popen.stdout, title), daemon=True)
            stderr_thread = threading.Thread(target=self._read_stream, args=(popen.stderr, title), daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            # Wait for the process and handle completion
            t = threading.Thread(target=self._pipe_reader, args=(popen, title), daemon=True)
            t.start()

        except FileNotFoundError as e:
            messagebox.showerror("Executable not found", f"Command executable not found: {e}")
            self._log(f"Executable not found: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start process: {e}")
            self._log(f"Failed to start process: {e}")

    def _read_stream(self, stream, title: str):
        try:
            for line in iter(stream.readline, b""):
                if not line:
                    break
                try:
                    decoded = line.decode(errors='ignore')
                    self._append_log(f"[{title}] {decoded}")
                except Exception:
                    pass
        except Exception:
            pass

    def _pipe_reader(self, popen: subprocess.Popen, title: str):
        # Wait for process to finish and log
        popen.wait()
        self._append_log(f"Process '{title}' exited with code {popen.returncode}\n")

        if title == "device-record" and self._device_record_device_path:
            try:
                self._log("Pulling recorded file from device...")
                pull_cmd = [self._get_adb_executable(), "pull", self._device_record_device_path, self._device_record_local_path]
                res = subprocess.run(pull_cmd, capture_output=True, text=True, timeout=300)
                if res.returncode == 0:
                    self._log(f"Device recording pulled to: {self._device_record_local_path}")
                else:
                    self._log(f"Failed to pull recording: {res.stderr.strip()}")
            except Exception as e:
                self._log(f"Error pulling device recording: {e}")
            finally:
                self._device_record_device_path = None
                self._device_record_local_path = None

    def _on_stop(self):
        if self.proc and self.proc.is_running():
            self._log(f"Stopping process: {self.proc.title}")
            try:
                self.proc.terminate()
            except Exception as e:
                self._log(f"Error stopping: {e}")
        else:
            self._log("No running process to stop.")

    def _on_close(self):
        # Stop monitoring
        self.monitoring = False
        # Stop any running process
        if self.proc and self.proc.is_running():
            try:
                self.proc.terminate()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = ctk.CTk()
    app = GamingHubApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

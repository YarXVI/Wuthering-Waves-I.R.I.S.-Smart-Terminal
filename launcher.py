"""
iris Service Launcher - Manages API server + desktop frontend lifecycle, shows real-time debug logs
Does not bundle server code, depends on system Python environment.
Can be packaged as standalone exe: pyinstaller --onefile --console launcher.py
"""
import sys
import os
import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime

# Determine project root directory
_script_dir = Path(sys.argv[0] if getattr(sys, 'frozen', False) else __file__).resolve().parent
ROOT = _script_dir.parent if _script_dir.name == "dist" else _script_dir
API_PORT = 8000
VITE_PORT = 5173


def log(msg: str, tag: str = "LAUNCHER"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}][{tag}] {msg}", flush=True)


def find_python() -> str:
    """Find available python command"""
    for cmd in [sys.executable, "python", "python3"]:
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5, encoding='utf-8', errors='replace')
            if r.returncode == 0:
                return cmd
        except Exception:
            continue
    return ""


def kill_process_by_port(port: int):
    """Try to kill process occupying specified port"""
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, encoding='utf-8', errors='replace')
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >=5 and parts[-1].isdigit():
                        try:
                            pid = int(parts[-1])
                            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                          capture_output=True, check=False)
                        except Exception:
                            pass
        except Exception:
            pass


def wait_for_health(url: str, timeout: int =30) -> bool:
    import urllib.request
    for i in range(timeout):
        try:
            r = urllib.request.urlopen(url, timeout=2)
            if r.status == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def print_banner():
    print("""

   iris - Virtual Office

  API:       http://127.0.0.1:8000
  Frontend:  http://localhost:5173
  Meeting:   http://127.0.0.1:8000/meeting

  Logs below. Close window to stop all.

""" + "-" * 60)


def main():
    print_banner()

    # -- Environment Check --
    if not (ROOT / ".env").exists():
        log(".env not found! Copy .env.example and fill in API Key.", "ERROR")
        input("\nPress Enter to exit...")
        return 1

    python_cmd = find_python()
    if not python_cmd:
        log("Python not found in PATH!", "ERROR")
        input("\nPress Enter to exit...")
        return 1

    # -- Cleanup Ports --
    log(f"Cleaning up ports {API_PORT} and {VITE_PORT}...", "INFO")
    kill_process_by_port(API_PORT)
    kill_process_by_port(VITE_PORT)
    time.sleep(2)

    # -- Start API Server --
    api_proc = subprocess.Popen(
        [python_cmd, "-m", "server.main"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        shell=sys.platform == "win32")
    log(f"API server started (PID {api_proc.pid})", "API")

    # Wait for API health check
    api_ok = wait_for_health(f"http://127.0.0.1:{API_PORT}/health")

    # -- Start Frontend --
    frontend_cwd = str(ROOT / "desktop")
    if sys.platform == "win32":
        frontend_cmd = ["npm.cmd", "run", "dev"]
    else:
        frontend_cmd = ["npm", "run", "dev"]

    ui_proc = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        shell=sys.platform == "win32")
    log(f"Frontend started (PID {ui_proc.pid})", "UI")

    if api_ok:
        log("=== All services started ===")
    else:
        log("=== API may not be ready ===", "ERROR")

    try:
        def monitor_process(proc, name):
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                if line.strip():
                    log(line.rstrip(), name)

        threading.Thread(target=monitor_process, args=(api_proc, "API"), daemon=True).start()
        threading.Thread(target=monitor_process, args=(ui_proc, "UI"), daemon=True).start()

        while True:
            time.sleep(1)

            if api_proc.poll() is not None:
                log("API server exited!", "ERROR")
                break
            if ui_proc.poll() is not None:
                log("Frontend server exited!", "ERROR")
                break
    except KeyboardInterrupt:
        pass

    # Cleanup
    log("Shutting down...")
    for p in [api_proc, ui_proc]:
        try:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except:
                    p.kill()
        except:
            pass
    kill_process_by_port(API_PORT)
    kill_process_by_port(VITE_PORT)
    log("All stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())

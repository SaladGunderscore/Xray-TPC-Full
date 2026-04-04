import os
import sys
import time
import signal
import subprocess
from typing import List, Tuple


# =========================
# CONFIG
# =========================

BRIDGE_FILES = [
    "twitch_to_stalker.py",
    "tpc_bits_bridge_test.py",
    "tpc_subs_bridge_test.py",
]


# =========================
# HELPERS
# =========================

def get_base_dir() -> str:
    return os.path.abspath(os.path.dirname(__file__))


def find_bridge_paths(base_dir: str) -> List[Tuple[str, str]]:
    found: List[Tuple[str, str]] = []

    for filename in BRIDGE_FILES:
        full_path = os.path.join(base_dir, filename)
        if os.path.exists(full_path):
            found.append((filename, full_path))
        else:
            print(f"[BRIDGE-LAUNCHER] Missing file: {filename}")

    return found


def launch_bridge(script_name: str, script_path: str) -> subprocess.Popen:
    print(f"[BRIDGE-LAUNCHER] Launching: {script_name}")

    return subprocess.Popen(
        [sys.executable, script_path],
        cwd=os.path.dirname(script_path),
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
    )


def terminate_processes(processes: List[Tuple[str, subprocess.Popen]]) -> None:
    print("[BRIDGE-LAUNCHER] Shutting down bridges...")

    for name, proc in processes:
        try:
            if proc.poll() is None:
                print(f"[BRIDGE-LAUNCHER] Terminating: {name}")
                proc.terminate()
        except Exception as e:
            print(f"[BRIDGE-LAUNCHER] Failed to terminate {name}: {e}")

    time.sleep(1.0)

    for name, proc in processes:
        try:
            if proc.poll() is None:
                print(f"[BRIDGE-LAUNCHER] Killing: {name}")
                proc.kill()
        except Exception as e:
            print(f"[BRIDGE-LAUNCHER] Failed to kill {name}: {e}")


# =========================
# MAIN
# =========================

def main() -> None:
    base_dir = get_base_dir()
    print(f"[BRIDGE-LAUNCHER] Base dir: {base_dir}")

    bridges = find_bridge_paths(base_dir)
    if not bridges:
        print("[BRIDGE-LAUNCHER] No bridge files found.")
        input("[BRIDGE-LAUNCHER] Press Enter to close...")
        return

    processes: List[Tuple[str, subprocess.Popen]] = []

    try:
        for script_name, script_path in bridges:
            proc = launch_bridge(script_name, script_path)
            processes.append((script_name, proc))

        print("[BRIDGE-LAUNCHER] All available bridges launched.")
        print("[BRIDGE-LAUNCHER] Press Ctrl+C to stop all bridges.")

        while True:
            for name, proc in processes:
                exit_code = proc.poll()
                if exit_code is not None:
                    print(f"[BRIDGE-LAUNCHER] Bridge exited: {name} (code {exit_code})")
            time.sleep(2.0)

    except KeyboardInterrupt:
        print("[BRIDGE-LAUNCHER] Ctrl+C received.")
    except Exception as e:
        print(f"[BRIDGE-LAUNCHER] ERROR: {e}")
    finally:
        terminate_processes(processes)


if __name__ == "__main__":
    main()
"""Run all KitchenGuard IoT components in separate processes."""
from __future__ import annotations

import subprocess
import sys
import time

SCRIPTS = [
    "data_manager.py",
    "actuator_emulator.py",
    "temperature_emulator.py",
    "gas_smoke_emulator.py",
    "gui_app.py",
]


def main() -> None:
    processes = []
    print("Starting KitchenGuard IoT project...")
    try:
        for script in SCRIPTS:
            print(f"Starting {script}")
            p = subprocess.Popen([sys.executable, script])
            processes.append(p)
            time.sleep(1)
        print("All components started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all components...")
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    main()

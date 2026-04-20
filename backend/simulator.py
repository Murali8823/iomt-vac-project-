"""
IoMT Device Simulator
=====================
Simulates 50 medical IoT devices, each producing realistic vital signs
(heart_rate, temp, resp_rate) every 2 seconds.  Anomalous spikes are
injected randomly (~8 % of readings) to exercise downstream anomaly-
detection pipelines.

Usage from main.py
------------------
    from simulator import get_device_data, start_simulation

    start_simulation()          # kicks off the background thread
    data = get_device_data()    # returns latest snapshot for all devices
"""

import json
import random
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
NUM_DEVICES: int = 50
UPDATE_INTERVAL: float = 2.0          # seconds

# Normal physiological ranges
HR_MIN, HR_MAX = 60, 120              # bpm
TEMP_MIN, TEMP_MAX = 36.0, 40.0      # °C
RESP_MIN, RESP_MAX = 12, 25          # breaths / min

# Anomaly injection
ANOMALY_PROBABILITY: float = 0.08    # ~8 % chance per device per tick

# Anomaly spike offsets (added / subtracted from current value)
HR_SPIKE = (30, 60)
TEMP_SPIKE = (2.0, 5.0)
RESP_SPIKE = (10, 20)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
STATUS_PATH = BASE_DIR / "project_status.json"

# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------
_device_data: List[Dict[str, Any]] = []
_lock = threading.Lock()
_running = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_status() -> dict:
    """Read the current project_status.json (or return empty dict)."""
    if not STATUS_PATH.exists():
        return {}
    try:
        with STATUS_PATH.open("r") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _write_status(key: str, value: Any) -> None:
    """Upsert a single key in project_status.json."""
    status = _read_status()
    status[key] = value
    with STATUS_PATH.open("w") as fh:
        json.dump(status, fh, indent=2)


def _generate_vitals(device_id: int) -> Dict[str, Any]:
    """
    Generate a single reading for *device_id*.

    With probability ANOMALY_PROBABILITY one of the three vitals will
    receive an anomalous spike (either up or down).
    """
    heart_rate = random.randint(HR_MIN, HR_MAX)
    temp = round(random.uniform(TEMP_MIN, TEMP_MAX), 1)
    resp_rate = random.randint(RESP_MIN, RESP_MAX)

    is_anomaly = False

    if random.random() < ANOMALY_PROBABILITY:
        is_anomaly = True
        # Choose which vital to spike
        spike_target = random.choice(["heart_rate", "temp", "resp_rate"])
        direction = random.choice([-1, 1])

        if spike_target == "heart_rate":
            heart_rate += direction * random.randint(*HR_SPIKE)
        elif spike_target == "temp":
            temp = round(temp + direction * random.uniform(*TEMP_SPIKE), 1)
        else:
            resp_rate += direction * random.randint(*RESP_SPIKE)

    return {
        "device_id": f"DEV-{device_id:03d}",
        "heart_rate": heart_rate,
        "temp": temp,
        "resp_rate": resp_rate,
        "is_anomaly": is_anomaly,
        "timestamp": time.time(),
    }


def _simulation_loop() -> None:
    """Background loop that refreshes all device data every UPDATE_INTERVAL."""
    global _running
    while _running:
        snapshot = [_generate_vitals(i) for i in range(1, NUM_DEVICES + 1)]
        with _lock:
            global _device_data
            _device_data = snapshot
        time.sleep(UPDATE_INTERVAL)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_device_data() -> List[Dict[str, Any]]:
    """
    Return the latest snapshot of simulated device readings.

    Returns a list of dicts, one per device:
        {
            "device_id": "DEV-001",
            "heart_rate": 78,
            "temp": 37.2,
            "resp_rate": 18,
            "is_anomaly": False,
            "timestamp": 1713636430.123
        }
    """
    with _lock:
        # Return a shallow copy so callers can't mutate the shared list
        return list(_device_data)


def start_simulation() -> None:
    """
    Start the simulation background thread (idempotent).

    Also sets ``simulation_ready: true`` in *project_status.json*.
    """
    global _running
    if _running:
        return

    _running = True

    # Seed the store immediately so get_device_data() never returns []
    initial = [_generate_vitals(i) for i in range(1, NUM_DEVICES + 1)]
    with _lock:
        global _device_data
        _device_data = initial

    thread = threading.Thread(target=_simulation_loop, daemon=True)
    thread.start()

    # Mark simulation as ready in project status
    _write_status("simulation_ready", True)


def stop_simulation() -> None:
    """Gracefully stop the simulation loop."""
    global _running
    _running = False


# ---------------------------------------------------------------------------
# Stand-alone quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    start_simulation()
    print(f"Simulator started — {NUM_DEVICES} devices, updating every {UPDATE_INTERVAL}s")
    try:
        while True:
            data = get_device_data()
            anomalies = [d for d in data if d["is_anomaly"]]
            print(
                f"[{time.strftime('%H:%M:%S')}] "
                f"Devices: {len(data)} | "
                f"Anomalies this tick: {len(anomalies)}"
            )
            if anomalies:
                for a in anomalies:
                    print(f"   [!] {a['device_id']}  HR={a['heart_rate']}  "
                          f"T={a['temp']}  RR={a['resp_rate']}")
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        stop_simulation()
        print("\nSimulator stopped.")

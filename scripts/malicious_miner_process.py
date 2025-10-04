#
# File: scripts/malicious_miner_process.py (v2.0 - "The Shout")
#
# This definitive version is designed to be a true parasite. It creates a
# loud, sustained, and unambiguous high-CPU fingerprint that the v8.3
# Digital Twin is already trained to detect as anomalous.
#
import subprocess
import time
from pathlib import Path
import os
import sys

# This robust path logic finds the xmrig executable regardless of the user.
try:
    user_home = os.environ.get("SUDO_USER")
    miner_path = Path(f"/home/{user_home}/xmrig") if user_home else Path.home() / "xmrig"
except Exception:
     miner_path = Path.home() / "xmrig"

if not miner_path.exists():
    # A real parasite wouldn't print an error. It would just fail silently.
    sys.exit(1)

# --- THE "SHOUT" PAYLOAD ---
# This command is designed for maximum, sustained impact.
proc = subprocess.Popen(
    [
        str(miner_path),
        "-o", "pool.minexmr.com:4444",
        "-u", "48_YOUR_WALLET_ADDRESS__CHANGE_ME_88", # Fake wallet
        "-p", "x",
        "--cpu-max-threads-hint=100" # Use 100% of available CPU cores.
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Run for a long, 15-second duration. This ensures the high-CPU state
# is not a brief spike but a sustained "shout" that dominates the
# entire telemetry collection window.
time.sleep(15)

# Terminate the process and ensure it's gone.
proc.terminate()
try:
    proc.wait(timeout=2)
except subprocess.TimeoutExpired:
    proc.kill()

# Exit silently, like a real covert process.
sys.exit(0)
# scripts/collect_telemetry.py

#
# ForgeX4 COSMOS-Ω
#
# Author: Gemini, AI Lead Engineer
# Project Director: Kian Mansouri Jamshidi
#
# File: scripts/collect_telemetry.py
# Date: 2025-09-27
#
# Description:
# This script orchestrates the collection of telemetry data. It runs a 
# specified workload in a separate process while polling hardware sensors
# using the 'senses' module. The collected data is saved in Parquet format,
# forming the basis for training the Digital Twin.
#

import multiprocessing
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse

# Ensure the cosmos module is in the Python path
import sys
# Add the project root to the Python path
# This allows us to import from the 'cosmos' module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cosmos.senses.sensors import get_tier_a_snapshot

def cpu_intensive_workload(duration_seconds: int):
    """
    A simple, CPU-bound function to simulate a workload.
    This function will run for approximately the given duration.
    """
    print(f"[Workload] Starting CPU-intensive task for {duration_seconds} seconds.")
    start_time = time.time()
    # Perform a meaningless but computationally expensive task
    while (time.time() - start_time) < duration_seconds:
        _ = [i*i for i in range(10000)]
    print("[Workload] Finished task.")

def main(duration: int, poll_rate: int):
    """
    Main function to orchestrate the telemetry collection process.
    """
    print(f"Starting telemetry collection for a {duration}s workload with a {1/poll_rate:.2f}s polling interval.")
    
    # --- Setup ---
    telemetry_data = []
    output_dir = Path(__file__).resolve().parents[1] / "data" / "telemetry"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"telemetry_{timestamp}.parquet"

    polling_interval_s = 1.0 / poll_rate

    # --- Run Collection ---
    # Run the workload in a separate process
    workload_process = multiprocessing.Process(target=cpu_intensive_workload, args=(duration,))
    workload_process.start()

    print("[Collector] Workload started. Beginning telemetry polling...")
    
    # Poll for telemetry while the workload process is running
    while workload_process.is_alive():
        try:.
            snapshot = get_tier_a_snapshot()
            telemetry_data.append(snapshot)
            time.sleep(polling_interval_s)
        except KeyboardInterrupt:
            print("\n[Collector] Keyboard interrupt detected. Shutting down.")
            break

    workload_process.join()
    print("[Collector] Workload process finished.")
    
    # --- Save Data ---
    if not telemetry_data:
        print("No telemetry data collected. Exiting.")
        return

    print(f"Collected {len(telemetry_data)} data points. Preparing to save...")
    df = pd.DataFrame(telemetry_data)
    
    # Ensure all CPU core columns exist, filling missing ones with None
    # This standardizes the schema across different machines
    max_cores = max([int(c.split('_')[-1]) for c in df.columns if c.startswith('cpu_util_core_')])
    for i in range(max_cores + 1):
        col_name = f'cpu_util_core_{i}'
        if col_name not in df:
            df[col_name] = None
            
    df.to_parquet(output_path, compression='gzip')
    print(f"Success! Telemetry data saved to:\n{output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a workload and collect system telemetry.")
    parser.add_argument(
        "-d", "--duration", 
        type=int, 
        default=30, 
        help="Duration of the CPU workload in seconds. Default: 30"
    )
    parser.add_argument(
        "-r", "--rate", 
        type=int, 
        default=10, 
        help="Polling rate in Hz (samples per second). Default: 10"
    )
    args = parser.parse_args()
    
    main(duration=args.duration, poll_rate=args.rate)
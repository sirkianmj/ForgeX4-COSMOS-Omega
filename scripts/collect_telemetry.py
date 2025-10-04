# scripts/collect_telemetry.py

#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: scripts/collect_telemetry.py
# Date: 2025-09-27
#
# Description:
# This is the master script for collecting labeled, multi-workload telemetry data
# It can invoke different workload simulators (CPU, I/O, memory, etc.)
# and records a 'workload_type' label for each run, creating a rich dataset
# for training the Digital Twin v2.0.
#

import multiprocessing
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse
import importlib

# Ensure the cosmos and scripts modules are in the Python path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.senses.sensors import get_tier_a_snapshot

def workload_runner(workload_type: str, duration: int):
    """
    Dynamically imports and runs the specified workload function.
    """
    try:
        module_path = f"scripts.workloads.{workload_type}"
        workload_module = importlib.import_module(module_path)
        
        # We assume a standard function name like 'run_cpu_bound_workload'
        # Let's find the function in that module
        run_function_name = f"run_{workload_type}_workload"
        run_function = getattr(workload_module, run_function_name)
        
        # Some workloads need the temp directory
        if workload_type == "io_bound":
            temp_dir = PROJECT_ROOT / "temp"
            temp_dir.mkdir(exist_ok=True)
            run_function(duration_seconds=duration, temp_dir=temp_dir)
        else:
            run_function(duration_seconds=duration)

    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error: Could not find or run workload '{workload_type}'. Check the module and function names.")
        print(e)
        # Add a simple CPU-bound workload as a fallback
        print("Running a simple CPU-bound workload as a fallback.")
        start_time = time.time()
        while (time.time() - start_time) < duration:
            _ = [i*i for i in range(10000)]

def main(duration: int, poll_rate: int, workload: str):
    """
    Main function to orchestrate the labeled telemetry collection process.
    """
    print(f"--- Telemetry Collection Run ---")
    print(f"Workload Type: {workload}")
    print(f"Duration:      {duration}s")
    print(f"Poll Rate:     {poll_rate} Hz")
    print("---------------------------------")
    
    # --- Setup ---
    telemetry_data = []
    output_dir = PROJECT_ROOT / "data" / "telemetry_v2" # New directory for the new data
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{workload}_{timestamp}.parquet"

    polling_interval_s = 1.0 / poll_rate

    # --- Run Collection ---
    workload_process = multiprocessing.Process(target=workload_runner, args=(workload, duration))
    workload_process.start()

    print("[Collector] Workload started. Beginning telemetry polling...")
    
    while workload_process.is_alive():
        try:
            snapshot = get_tier_a_snapshot()
            telemetry_data.append(snapshot)
            time.sleep(polling_interval_s)
        except KeyboardInterrupt:
            print("\n[Collector] Keyboard interrupt detected. Shutting down.")
            break

    workload_process.join()
    print("[Collector] Workload process finished.")
    
    if not telemetry_data:
        print("No telemetry data collected. Exiting.")
        return

    print(f"Collected {len(telemetry_data)} data points. Preparing to save...")
    df = pd.DataFrame(telemetry_data)
    
    # Add the crucial 'workload_type' label
    df['workload_type'] = workload
    
    # Standardize schema
    core_cols = [c for c in df.columns if c.startswith('cpu_util_core_')]
    if core_cols:
        max_cores = max([int(c.split('_')[-1]) for c in core_cols])
        for i in range(max_cores + 1):
            col_name = f'cpu_util_core_{i}'
            if col_name not in df:
                df[col_name] = None
            
    df.to_parquet(output_path, compression='gzip')
    print(f"\nSuccess! Labeled telemetry data saved to:\n{output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a labeled workload and collect system telemetry.")
    # Renamed the old CPU workload to 'cpu_bound'
    WORKLOAD_CHOICES = ['cpu_bound', 'io_bound', 'memory_bound', 'mixed_workload', 'network_bound']
    
    parser.add_argument(
        "-w", "--workload",
        type=str,
        required=True,
        choices=WORKLOAD_CHOICES,
        help="The type of workload to run."
    )
    parser.add_argument(
        "-d", "--duration", 
        type=int, 
        default=60, 
        help="Duration of the workload in seconds. Default: 60"
    )
    parser.add_argument(
        "-r", "--rate", 
        type=int, 
        default=10, 
        help="Polling rate in Hz (samples per second). Default: 10"
    )
    args = parser.parse_args()
    
    # We need a CPU-bound script for the new structure to work
    # Let's rename the old function and put it in its own file
    
    # First, create cpu_bound.py
    cpu_bound_script_path = PROJECT_ROOT / "scripts" / "workloads" / "cpu_bound.py"
    if not cpu_bound_script_path.exists():
        with open(cpu_bound_script_path, "w") as f:
            f.write(
"""# scripts/workloads/cpu_bound.py
import time

def run_cpu_bound_workload(duration_seconds: int):
    print(f"[Workload:CPU] Starting CPU-intensive task for {duration_seconds} seconds.")
    start_time = time.time()
    while (time.time() - start_time) < duration_seconds:
        _ = [i*i for i in range(10000)]
    print("[Workload:CPU] Finished task.")

if __name__ == '__main__':
    run_cpu_bound_workload(duration_seconds=10)
"""
            )
        print("Created 'cpu_bound.py' workload script.")

    main(duration=args.duration, poll_rate=args.rate, workload=args.workload)
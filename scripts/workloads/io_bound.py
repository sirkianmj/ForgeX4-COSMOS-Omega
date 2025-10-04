# scripts/workloads/io_bound.py

import os
import time
import uuid
from pathlib import Path

def run_io_bound_workload(duration_seconds: int, temp_dir: Path):
    """
    Simulates an I/O-bound workload by creating, writing to, reading from,
    and deleting many small temporary files.

    Args:
        duration_seconds: The approximate duration to run the workload.
        temp_dir: The directory to perform file operations in.
    """
    print(f"[Workload:IO] Starting I/O-bound task for {duration_seconds} seconds.")
    start_time = time.time()
    files_created = []

    # Ensure the temp directory for this workload exists
    workload_temp_dir = temp_dir / "io_workload"
    workload_temp_dir.mkdir(exist_ok=True)
    
    # Some dummy data to write
    dummy_data = b"ForgeX4 COSMOS-Omega Digital Twin Telemetry Data." * 10

    try:
        while (time.time() - start_time) < duration_seconds:
            # Create a few files
            for _ in range(5):
                file_path = workload_temp_dir / f"temp_{uuid.uuid4()}.tmp"
                with open(file_path, "wb") as f:
                    f.write(dummy_data)
                files_created.append(file_path)

            # Read a few files
            for i in range(min(5, len(files_created))):
                file_to_read = files_created[i]
                with open(file_to_read, "rb") as f:
                    _ = f.read()

            # Delete a few files to keep the total number from exploding
            if len(files_created) > 50:
                for _ in range(5):
                    file_to_delete = files_created.pop(0)
                    os.remove(file_to_delete)
    
    finally:
        # Clean up all created files
        for file_path in files_created:
            if os.path.exists(file_path):
                os.remove(file_path)
        print("[Workload:IO] Finished task and cleaned up temporary files.")

if __name__ == '__main__':
    # A simple test case
    project_root = Path(__file__).resolve().parents[2]
    temp_directory = project_root / "temp"
    temp_directory.mkdir(exist_ok=True)
    run_io_bound_workload(duration_seconds=10, temp_dir=temp_directory)
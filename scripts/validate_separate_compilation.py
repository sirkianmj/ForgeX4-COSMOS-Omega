# scripts/validate_separate_compilation.py
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# Description:
# [UPDATED] Validates our "Separate Compilation" approach using the new,
# clean cronos_v0.2.c baseline defender.
#

import os
import sys
import subprocess
import tempfile
import shutil

# --- Configuration ---
RISCV_COMPILER = "riscv64-linux-gnu-gcc"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_SOURCE_PATH = os.path.join(PROJECT_ROOT, "data/genomes/cjson/cJSON.c")
APP_HEADER_DIR = os.path.join(PROJECT_ROOT, "data/genomes/cjson")

# Use the new, clean defender genome
DEFENDER_SOURCE_PATH = os.path.join(PROJECT_ROOT, "data/genomes/cronos/cronos_v0.2.c")
# Use a simple test harness that calls the new defender function
TEST_HARNESS_PATH = os.path.join(PROJECT_ROOT, "data/genomes/uranus/uranus_v1.0.c")

def main():
    """
    Validates the separate compilation and linking of the cJSON application,
    the v0.2 defender, and a test harness.
    """
    print("--- COSMOS-Ω: Separate Compilation Validation Test (v0.2) ---")

    # 1. Verify all required source files exist
    print("\n[PHASE 1] Verifying source files...")
    sources = [APP_SOURCE_PATH, DEFENDER_SOURCE_PATH, TEST_HARNESS_PATH]
    for src in sources:
        if not os.path.exists(src):
            print(f"  [FATAL ERROR] Required source file not found: {src}")
            return
    print("  [SUCCESS] All source files present.")

    # 2. Compile and Link all sources together
    print("\n[PHASE 2] Compiling and linking all components...")
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "a.out")
        
        compile_command = [
            RISCV_COMPILER,
            "-o", output_path,
            APP_SOURCE_PATH,
            DEFENDER_SOURCE_PATH,
            TEST_HARNESS_PATH,
            f"-I{APP_HEADER_DIR}"
        ]
        
        print(f"  Running command: {' '.join(compile_command)}")
        result = subprocess.run(compile_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  [SUCCESS] Compilation and linking successful!")
            print(f"  Final binary created at: {output_path}")
            print("\n--- NEW BASELINE ESTABLISHED: TEST PASSED ---")
        else:
            print("  [FAILURE] Compilation failed.")
            print("\n--- FOCUSED COMPILER ERRORS ---")
            print(result.stderr)
            print("\n--- TEST FAILED ---")

if __name__ == "__main__":
    main()
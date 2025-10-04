#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# File: scripts/debug_parser.py
#
# Description:
# [PARSER DIAGNOSTIC TOOL] A robust debugging system to find the root cause
# of the "typedef flood." It isolates the C preprocessor step, records the
# exact command being run, and saves the complete, raw output for forensic
# analysis. This will provide definitive evidence of the parser's behavior.
#

import os
import sys
import subprocess
import pycparser

# --- Setup Project Root Path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Configuration ---
TARGET_C_FILE = "data/genomes/cronos/cronos_v0.2.c"
OUTPUT_FILE = "artifacts/parser_debug_output.c"

def get_pycparser_fake_libc_path():
    """Finds the path to pycparser's fake libc includes."""
    return os.path.join(os.path.dirname(pycparser.__file__), 'utils/fake_libc_include')

def main():
    """Runs the parser diagnostic."""
    print("="*80)
    print("                PARSER DIAGNOSTIC TOOL ACTIVATED")
    print("="*80)

    c_file_path = os.path.join(project_root, TARGET_C_FILE)
    output_path = os.path.join(project_root, OUTPUT_FILE)
    fake_libc_path = get_pycparser_fake_libc_path()

    if not os.path.exists(c_file_path):
        print(f"FATAL: Target C file not found at: {c_file_path}")
        return

    print(f"1. Target C File: {c_file_path}")
    print(f"2. Pycparser Fake Libc Path: {fake_libc_path}")

    # --- Construct the exact preprocessor command ---
    # This replicates the logic from our CParser class for direct analysis.
    cpp_command = [
        'gcc',
        '-E',                # Critical: Stop after preprocessing.
        '-nostdinc',         # Critical: Do not search system standard include directories.
        f'-I{fake_libc_path}', # Critical: Use pycparser's fake headers.
        c_file_path
    ]

    print("\n3. Executing the following command:")
    print(f"   $ {' '.join(cpp_command)}")

    # --- Execute and capture the output ---
    try:
        result = subprocess.run(cpp_command, capture_output=True, text=True, check=True)
        
        # --- Save the "Black Box" recording ---
        with open(output_path, "w") as f:
            f.write(result.stdout)
        
        print(f"\n4. SUCCESS: Preprocessor executed correctly.")
        print(f"   - The full, raw output has been saved to: {OUTPUT_FILE}")

        # --- Analyze the output for the "typedef flood" ---
        if "pthread_mutex_t" in result.stdout or "uintmax_t" in result.stdout:
            print("\n5. ANALYSIS: The 'typedef flood' IS PRESENT in the preprocessor output.")
            print("   - ROOT CAUSE: The '-nostdinc' flag is being ignored or overridden by the gcc environment.")
        else:
            print("\n5. ANALYSIS: The 'typedef flood' IS NOT PRESENT in the preprocessor output.")
            print("   - This means the preprocessor is working correctly.")
            print("   - ROOT CAUSE: The flood is being introduced later, inside the pycparser library itself.")

    except subprocess.CalledProcessError as e:
        print("\n4. FAILURE: The preprocessor command failed to execute.")
        print(f"   - Return Code: {e.returncode}")
        print("\n--- STDERR ---")
        print(e.stderr)
        print("--------------")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    print("\n" + "="*80)
    print("                PARSER DIAGNOSTIC COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
# scripts/debug_full_pipeline.py
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# Description:
# [DEFINITIVE DEBUGGER] This script performs a full, isolated pipeline test,
# mimicking the ExecutionTitan's process for the initial, un-mutated genomes.
# It loads, cleans, unparses, and attempts to compile. If compilation fails,
# it prints the full compiler error and dumps the generated source code,
# providing the final, definitive root cause analysis.
#

import os
import sys
import subprocess
import tempfile
import shutil
import copy

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser
from cosmos.parser.ast_cleaner import clean_ast

# --- Configuration (Mirrors ExecutionTitan) ---
RISCV_COMPILER = "riscv64-linux-gnu-gcc"
APP_SOURCE_PATH = os.path.join(project_root, "data/genomes/cjson/cJSON.c")
APP_HEADER_DIR = os.path.join(project_root, "data/genomes/cjson")
CRONOS_PATH = os.path.join(project_root, "data/genomes/cronos/cronos_v0.2.c")
URANUS_PATH = os.path.join(project_root, "data/genomes/uranus/uranus_v1.0.c")
HEADER_BLOCK = """
#include <stdio.h>
#include <string.h>
#include "cJSON.h"
"""

def main():
    print("--- [FULL PIPELINE DEBUGGER] ---")
    parser = CParser()
    
    # 1. Load Genomes
    print("\n[PHASE 1] Loading initial Cronos and Uranus ASTs...")
    try:
        cronos_ast = parser.parse_file(CRONOS_PATH)
        uranus_ast = parser.parse_file(URANUS_PATH, cpp_args=[f'-I{APP_HEADER_DIR}'])
        print("  [SUCCESS] ASTs loaded.")
    except Exception as e:
        return print(f"  [FATAL] Failed to parse initial genomes: {e}")

    # 2. Clean ASTs
    print("\n[PHASE 2] Cleaning ASTs with ast_cleaner...")
    cleaned_cronos_ast = clean_ast(copy.deepcopy(cronos_ast))
    cleaned_uranus_ast = clean_ast(copy.deepcopy(uranus_ast))
    print("  [SUCCESS] ASTs cleaned.")

    # 3. Unparse to C Code
    print("\n[PHASE 3] Unparsing cleaned ASTs to C code strings...")
    try:
        cronos_code = parser.unparse(cleaned_cronos_ast)
        uranus_code = parser.unparse(cleaned_uranus_ast)
        print("  [SUCCESS] Unparsing complete.")
    except Exception as e:
        return print(f"  [FATAL] Failed to unparse cleaned ASTs: {e}")
        
    # 4. Attempt Compilation
    print("\n[PHASE 4] Attempting to compile the final product...")
    with tempfile.TemporaryDirectory() as temp_dir:
        cronos_path_temp = os.path.join(temp_dir, "cronos.c")
        uranus_path_temp = os.path.join(temp_dir, "uranus.c")
        output_path = os.path.join(temp_dir, "a.out")
        
        # Write final C code to files for inspection
        final_cronos_code = HEADER_BLOCK + cronos_code
        final_uranus_code = HEADER_BLOCK + uranus_code
        with open(cronos_path_temp, "w") as f: f.write(final_cronos_code)
        with open(uranus_path_temp, "w") as f: f.write(final_uranus_code)
        
        compile_command = [
            RISCV_COMPILER, "-o", output_path,
            APP_SOURCE_PATH, cronos_path_temp, uranus_path_temp,
            f"-I{APP_HEADER_DIR}"
        ]
        
        result = subprocess.run(compile_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n--- [VERDICT] SUCCESS: The full pipeline is clean. ---")
            print("The error must be in the evolutionary loop itself.")
        else:
            print("\n--- [VERDICT] FAILURE: The initial pipeline is flawed. ---")
            print("\n--- DEFINITIVE COMPILER ERROR ---")
            print(result.stderr)
            print("\n--- DUMPING FAILED CRONOS.C ---")
            print(final_cronos_code)
            print("\n--- DUMPING FAILED URANUS.C ---")
            print(final_uranus_code)
            print("\n--- END OF REPORT ---")
            
if __name__ == "__main__":
    main()
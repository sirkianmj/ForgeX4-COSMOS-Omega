# scripts/run_cjson_foundry.py
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# Description:
# [DEFINITIVE VERSION] This final script resolves the 'redefinition' error.
# The cleaning logic is expanded to surgically remove both Typedefs and Struct
# definitions that originate from the application's own source files. This
# prevents duplicate definitions, as the compiler will get the canonical
# definitions from the '#include "cJSON.h"' in the header block.
#

import os
import sys
import subprocess
import tempfile
import shutil
import pycparser

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser
from pycparser import c_ast

# --- Configuration ---
RISCV_COMPILER = "riscv64-linux-gnu-gcc"
APP_SOURCE_PATH = os.path.join(project_root, "data/genomes/cjson/cJSON.c")
APP_HEADER_DIR = os.path.join(project_root, "data/genomes/cjson")
DEFENDER_SOURCE_PATH = os.path.join(project_root, "data/genomes/cronos/cronos_v0.1.c")

# This header block is the single source of truth for all definitions.
HEADER_BLOCK = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <float.h>
#include "cJSON.h" 
"""

def main():
    """
    Orchestrates the parsing, merging, and compilation with definitive cleaning logic.
    """
    print("--- COSMOS-Ω Foundry: cJSON Integration Test ---")

    # 1. Verify Environment
    print("\n[PHASE 1] Verifying environment...")
    if not shutil.which(RISCV_COMPILER): return print(f"  [ERROR] Compiler not found")
    if not os.path.exists(APP_SOURCE_PATH): return print(f"  [ERROR] App source not found")
    if not os.path.exists(DEFENDER_SOURCE_PATH): return print(f"  [ERROR] Defender source not found")
    print("  [SUCCESS] Environment verified.")
    
    # 2. Parse Genomes
    print("\n[PHASE 2] Parsing source code into ASTs...")
    parser = CParser()
    try:
        app_ast = parser.parse_file(APP_SOURCE_PATH, cpp_args=[f'-I{APP_HEADER_DIR}'])
        print(f"  [SUCCESS] Parsed application: {os.path.basename(APP_SOURCE_PATH)}")
        defender_ast = parser.parse_file(DEFENDER_SOURCE_PATH)
        print(f"  [SUCCESS] Parsed defender: {os.path.basename(DEFENDER_SOURCE_PATH)}")
    except Exception as e:
        return print(f"  [ERROR] Failed to parse source files. Aborting. Error: {e}")

    # 3. Combine and Apply Definitive Cleaning
    print("\n[PHASE 3] Combining and Cleaning Genomes...")
    combined_ast = app_ast
    combined_ast.ext.extend(defender_ast.ext)
    print("  [SUCCESS] Genomes combined.")
    
    # --- DEFINITIVE FIX: Remove ALL app-specific type/struct definitions ---
    # We remove any type definition or struct declaration that came from cJSON's
    # own files. The compiler will get these from the cJSON.h include instead.
    nodes_to_keep = []
    for node in combined_ast.ext:
        # Check if the node has coordinate info and originates from our target's directory
        if node.coord and APP_HEADER_DIR in node.coord.file:
            # If it's a type or struct definition from the target, skip it.
            if isinstance(node, (c_ast.Typedef, c_ast.Struct)):
                continue
        nodes_to_keep.append(node)
    
    nodes_removed = len(combined_ast.ext) - len(nodes_to_keep)
    combined_ast.ext = nodes_to_keep
    print(f"  [SUCCESS] Definitive cleaning complete. Removed {nodes_removed} app-specific definitions.")
    
    combined_source_code = parser.unparse(combined_ast)
    print("  [SUCCESS] Genomes unparsed to source.")

    # 4. Compile the Final Source
    print("\n[PHASE 4] Compiling final source for RISC-V target...")
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = os.path.join(temp_dir, "combined.c")
        output_path = os.path.join(temp_dir, "a.out")
        
        with open(source_path, "w") as f:
            f.write(HEADER_BLOCK)
            f.write(combined_source_code)
        
        compile_command = [
            RISCV_COMPILER,
            "-o", output_path,
            source_path,
            f"-I{APP_HEADER_DIR}"
        ]
        
        print(f"  Running command: {' '.join(compile_command)}")
        result = subprocess.run(compile_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  [SUCCESS] Compilation successful! Output binary created at: {output_path}")
            print("\n--- INTEGRATION TEST PASSED ---")
        else:
            print("  [FAILURE] Compilation failed.")
            print("\n--- Compiler Errors ---")
            print(result.stderr)
            print("\n--- INTEGRATION TEST FAILED ---")

if __name__ == "__main__":
    main()
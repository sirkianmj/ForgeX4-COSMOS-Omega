# scripts/debug_initial_state.py
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# Description:
# [PRE-FLIGHT CHECK] This debug script tests the initial state of the
# genomes. It loads, cleans, and attempts to unparse the initial Cronos and
# Uranus genomes in isolation to verify the integrity of the cleaning process
# before evolution begins.
#

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser
from cosmos.parser.ast_cleaner import clean_ast

CRONOS_PATH = "data/genomes/cronos/cronos_v0.2.c"
URANUS_PATH = "data/genomes/uranus/uranus_v1.0.c"

def main():
    print("--- [PRE-FLIGHT CHECK] Initial Genome State Analysis ---")
    parser = CParser()
    
    for name, path in [("Cronos", CRONOS_PATH), ("Uranus", URANUS_PATH)]:
        print(f"\n--- Analyzing {name} Genome ---")
        try:
            # 1. Load
            ast = parser.parse_file(os.path.join(project_root, path), cpp_args=['-Idata/genomes/cjson'])
            num_typedefs_before = sum(1 for node in ast.ext if 'Typedef' in type(node).__name__)
            print(f"  [PHASE 1] LOAD: Success. Found {num_typedefs_before} typedefs.")

            # 2. Clean
            cleaned_ast = clean_ast(ast)
            num_typedefs_after = sum(1 for node in cleaned_ast.ext if 'Typedef' in type(node).__name__)
            print(f"  [PHASE 2] CLEAN: Success. Found {num_typedefs_after} typedefs remaining.")

            # 3. Unparse
            code = parser.unparse(cleaned_ast)
            print(f"  [PHASE 3] UNPARSE: Success.")
            if len(code) > 50:
                 print("    - Unparsed code looks plausible (length > 50).")

        except Exception as e:
            print(f"  [!!! FAILURE !!!] Pre-flight check failed for {name}.")
            print(f"    - Exception: {type(e).__name__} - {e.args}")
            return
            
    print("\n--- [PRE-FLIGHT CHECK] VERDICT: SUCCESS ---")
    print("Initial genomes can be loaded, cleaned, and unparsed without error.")

if __name__ == "__main__":
    main()
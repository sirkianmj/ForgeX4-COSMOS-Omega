# scripts/debug_mutation_pipeline.py
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# Description:
# [DEFINITIVE DEBUGGING TOOL] This script acts as a "separate machine" to
# forensically analyze the entire mutation pipeline, as directed. It performs
# one single mutation and provides a step-by-step log, including dumping the
# AST before and after, and the final C code. This will reveal the definitive
# root cause of the mutation failure.
#

import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser
from cosmos.foundry.mutations import hardening
from cosmos.parser.ast_cleaner import clean_ast

# --- Configuration ---
TARGET_GENOME_PATH = "data/genomes/cronos/cronos_v0.2.c"

def main():
    print("--- [DEBUG TITAN] Forensic Mutation Pipeline Analysis ---")
    
    # 1. Load the original genome
    print("\n[PHASE 1] Loading original genome...")
    parser = CParser()
    try:
        original_ast = parser.parse_file(os.path.join(project_root, TARGET_GENOME_PATH))
        print("  [SUCCESS] Original AST loaded.")
    except Exception as e:
        print(f"  [FATAL] Could not parse genome. Error: {e}")
        return

    # 2. Print the original code for baseline
    print("\n[PHASE 2] Unparsing original code (pre-mutation)...")
    original_code = parser.unparse(clean_ast(original_ast))
    print("-" * 25 + " ORIGINAL CODE " + "-" * 25)
    print(original_code)
    print("-" * 67)
    
    # 3. Apply the mutation
    print("\n[PHASE 3] Applying 'mutate_gets_to_fgets'...")
    mutated_ast = hardening.mutate_gets_to_fgets(original_ast)
    print("  [INFO] Mutation function executed.")
    
    # 4. Forensically compare the ASTs
    print("\n[PHASE 4] Comparing ASTs...")
    if original_ast == mutated_ast:
        print("  [!!! FAILURE !!!] The mutation function did NOT change the AST.")
        print("  This is the ROOT CAUSE. The AST is being returned unmodified.")
    else:
        print("  [SUCCESS] The mutation function correctly created a NEW AST object.")

    # 5. Print the mutated code
    print("\n[PHASE 5] Unparsing mutated code (post-mutation)...")
    mutated_code = parser.unparse(clean_ast(mutated_ast))
    print("-" * 25 + " MUTATED CODE " + "-" * 26)
    print(mutated_code)
    print("-" * 67)
    
    # 6. Final analysis
    print("\n[PHASE 6] Final Analysis...")
    if "fgets" in mutated_code:
        print("  [VERDICT] SUCCESS: The final code contains 'fgets'.")
    else:
        print("  [VERDICT] FAILURE: The final code STILL contains 'gets'.")
        print("  This confirms the mutation is ineffective at the code level.")

if __name__ == "__main__":
    main()
#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: scripts/validate_ledger_sprint7.py
# Date: 2025-09-28
#
# Description:
# [VERSION 2.1 - DEBUG TRACE] This version is instrumented with print
# statements to debug a silent execution failure. It will trace the
# import and execution flow to identify the exact point of the hang.
#

# --- TRACE POINT 0: Script execution begins ---
print("[TRACE] Script execution started.")

import os
import sys

# --- TRACE POINT 1: Standard libraries imported ---
print("[TRACE] os, sys imported.")

# Ensure the cosmos package is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("[TRACE] System path modified.")

# --- TRACE POINT 2: Attempting to import from cosmos.parser.parser ---
print("[TRACE] Attempting to import 'parse_c_file_to_ast'...")
from cosmos.parser.parser import parse_c_file_to_ast
print("[TRACE] SUCCESS: Imported 'parse_c_file_to_ast'.")

# --- TRACE POINT 3: Attempting to import from cosmos.foundry.foundry ---
print("[TRACE] Attempting to import 'Foundry'...")
from cosmos.foundry.foundry import Foundry
print("[TRACE] SUCCESS: Imported 'Foundry'.")


def main():
    """Main validation function."""
    # --- TRACE POINT 4: main() function entered ---
    print("[TRACE] main() function entered.")
    print("="*80)
    print("= Starting Validation for Sprint 7: Explainability Ledger Prototype =")
    print("="*80)

    # 1. Define paths to initial genomes
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cronos_path = os.path.join(project_root, "data", "genomes", "cronos", "cronos_v0.1.c")
    gaia_path = os.path.join(project_root, "data", "genomes", "gaia", "gaia_v0.1.c")

    print(f"\n[1] Loading initial genomes...")
    print(f"  - Cronos (Defender): {cronos_path}")
    print(f"  - Gaia (Application): {gaia_path}")

    if not os.path.exists(cronos_path) or not os.path.exists(gaia_path):
        print("\nError: Genome files not found. Please ensure paths are correct.")
        return

    # 2. Parse the source code into ASTs using the correct function
    print("\n[2] Parsing source files into ASTs...")
    try:
        initial_cronos_ast = parse_c_file_to_ast(cronos_path)
        initial_gaia_ast = parse_c_file_to_ast(gaia_path)
        print("  - Parsing complete.")
    except Exception as e:
        print(f"\n  - FATAL ERROR during parsing: {e}")
        print("  - Validation cannot continue.")
        return

    # 3. Configure a minimal, fast foundry run
    config = {
        "population_size": 4,
        "generations": 2,
        "mutation_rate": 0.75,
        "elitism_count": 1,
        "parallel_workers": 2,
        "output_dir": "artifacts"
    }
    print("\n[3] Configuring a minimal foundry for a rapid test run:")
    for key, value in config.items():
        print(f"  - {key}: {value}")

    # 4. Instantiate and run the foundry
    print("\n[4] Initializing the Foundry...")
    foundry = Foundry(
        initial_cronos_ast=initial_cronos_ast,
        initial_uranus_ast=initial_gaia_ast,
        config=config
    )

    print("\n[5] Starting the evolutionary run. This will test the ledger integration.")
    champion = foundry.run_evolution()

    # 6. Final validation check
    print("\n[6] Validation Concluding...")
    if champion and champion['genome']:
        print("  - Foundry run completed successfully.")
        print(f"  - Final champion fitness: {champion['fitness']:.4f}")

        log_path = foundry.ledger.output_path
        if os.path.exists(log_path):
            print(f"  - SUCCESS: Ledger file was created at: {log_path}")
            print("  - Please inspect the file to confirm its contents are correct.")
        else:
            print(f"  - FAILURE: Ledger file was NOT created at the expected path: {log_path}")
    else:
        print("  - FAILURE: The foundry run did not produce a valid champion.")

    print("\n" + "="*80)
    print("= Validation Complete =")
    print("="*80)

# --- TRACE POINT 5: Checking if script is run as main ---
print("[TRACE] Checking __name__ == '__main__'.")
if __name__ == "__main__":
    # --- TRACE POINT 6: Calling main() ---
    print("[TRACE] __name__ is '__main__', calling main().")
    main()
else:
    print(f"[TRACE] Script was imported, not run directly (__name__ is {__name__}).")
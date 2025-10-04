#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: scripts/run_minimal_foundry.py
# Date: 2025-09-27
#
# Description:
# This script is the main entry point for launching the COSMOS-Ω co-evolutionary
# foundry. It initializes the defender (Cronos) and attacker (Uranus)
# populations from source files, configures the evolutionary run,
# executes the foundry, and saves the resulting champion defender.
#

import sys
import os

# --- Add the project root to the Python path ---
# This allows us to import from the 'cosmos' package without installation.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from cosmos.foundry.foundry import Foundry
from cosmos.parser import parser

# --- Configuration ---
CONFIG = {
    "population_size": 20,
    "generations": 10,
    "mutation_rate": 0.25,
    "elitism_count": 2,
}

# --- Genome Source Files ---
# We now define the starting point for both the defender and the attacker.
# These files must exist for the script to run.
CRONOS_INITIAL_GENOME_PATH = "data/genomes/cronos/cronos_v1.0.c"
URANUS_INITIAL_GENOME_PATH = "data/genomes/uranus/uranus_v1.0.c"
CHAMPION_OUTPUT_PATH = "artifacts/phase2/champion_defender_sprint6.c"

def main():
    """Main execution function for the co-evolutionary run."""
    print("="*50)
    print("  ForgeX4 COSMOS-Ω: Co-Evolutionary Foundry Run")
    print("="*50)

    # --- Step 1: Load Initial Genomes ---
    print(f"Loading initial Cronos (defender) genome from: {CRONOS_INITIAL_GENOME_PATH}")
    try:
        # Note: Ensure you have a 'parse_file_to_ast' or similar function in your parser module
        initial_cronos_ast = parser.parse_c_file_to_ast(CRONOS_INITIAL_GENOME_PATH)
    except Exception as e:
        print(f"Fatal Error: Could not parse Cronos source file. Details: {e}")
        sys.exit(1)

    print(f"Loading initial Uranus (attacker) genome from: {URANUS_INITIAL_GENOME_PATH}")
    try:
        initial_uranus_ast = parser.parse_c_file_to_ast(URANUS_INITIAL_GENOME_PATH)
    except Exception as e:
        print(f"Fatal Error: Could not parse Uranus source file. Details: {e}")
        sys.exit(1)

    # --- Step 2: Initialize and Run the Foundry ---
    print("\nInitializing the Co-Evolutionary Foundry...")
    foundry_engine = Foundry(
        initial_cronos_ast=initial_cronos_ast,
        initial_uranus_ast=initial_uranus_ast,
        config=CONFIG
    )

    print("\nStarting the evolutionary run...")
    champion_defender = foundry_engine.run()

    # --- Step 3: Save the Champion Defender ---
    if champion_defender and champion_defender.get('genome'):
        print(f"\nEvolution complete. Saving champion defender to: {CHAMPION_OUTPUT_PATH}")
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(CHAMPION_OUTPUT_PATH), exist_ok=True)
        
        try:
            # Unparse the final champion AST back to C code
            champion_code = parser.unparse_ast_to_c(champion_defender['genome'])
            
            # Add standard headers for completeness and portability
            headers = '#include <stdio.h>\n#include <string.h>\n\n'
            final_code = headers + champion_code

            with open(CHAMPION_OUTPUT_PATH, "w") as f:
                f.write(final_code)
            print("Champion saved successfully.")

        except Exception as e:
            print(f"Error: Could not save the champion file. Details: {e}")
    else:
        print("\nEvolutionary run finished, but no viable champion defender was produced.")
    
    print("\n" + "="*50)
    print("  Run Concluded.")
    print("="*50)

if __name__ == "__main__":
    main()
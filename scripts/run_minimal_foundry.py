#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: scripts/run_minimal_foundry.py
# Date: 2025-09-25
#
# Description:
# This script serves as the entry point for running a minimal, end-to-end
# test of the evolutionary foundry. It loads the initial genomes, configures
# the foundry, and kicks off the evolutionary process.
#
import os
import sys

# Ensure the 'cosmos' package can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cosmos.parser import parser
from cosmos.foundry import foundry

# --- Configuration ---
INITIAL_GENOME_PATH = "data/genomes/gaia/gaia_v0.1.c" # We'll evolve Gaia directly for now

FOUNDRY_CONFIG = {
    "population_size": 10,
    "mutation_rate": 0.2,  # A higher rate to ensure we see mutations happen
    "generations": 5,
}

def main():
    """Main execution function."""
    print("--- Minimal Viable Foundry Run ---")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, INITIAL_GENOME_PATH)

    print(f"Loading initial genome from: {file_path}")
    initial_ast = parser.parse_c_file_to_ast(file_path)

    print("Initializing the Foundry...")
    engine = foundry.Foundry(initial_ast, FOUNDRY_CONFIG)

    print("Starting the evolutionary run...")
    engine.run()

if __name__ == '__main__':
    main()
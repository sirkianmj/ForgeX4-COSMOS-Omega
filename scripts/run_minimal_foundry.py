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
# This script runs the minimal foundry and forges the final champion artifact.
#
import os
import sys

# Ensure the 'cosmos' package can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cosmos.parser import parser
from cosmos.foundry import foundry
from cosmos.forge import forge # <-- NEW IMPORT

# --- Configuration ---
INITIAL_GENOME_PATH = "data/genomes/gaia/gaia_v0.1.c"
CHAMPION_ARTIFACT_PATH = "artifacts/phase1/champion_v0.1.c" # <-- NEW

FOUNDRY_CONFIG = {
    "population_size": 20,  # Increased for higher chance of finding a champion
    "mutation_rate": 0.2,
    "generations": 5,
}

def main():
    """Main execution function."""
    print("--- Minimal Viable Foundry Run ---")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    initial_file_path = os.path.join(project_root, INITIAL_GENOME_PATH)
    output_artifact_path = os.path.join(project_root, CHAMPION_ARTIFACT_PATH)

    print(f"Loading initial genome from: {initial_file_path}")
    initial_ast = parser.parse_c_file_to_ast(initial_file_path)

    print("Initializing the Foundry...")
    engine = foundry.Foundry(initial_ast, FOUNDRY_CONFIG)

    print("Starting the evolutionary run...")
    champion = engine.run()

    # --- NEW: Forge the champion at the end of the run ---
    if champion['genome']:
        forge.forge_champion(champion['genome'], output_artifact_path)
    else:
        print("Evolutionary run finished with no viable champion.")


if __name__ == '__main__':
    main()
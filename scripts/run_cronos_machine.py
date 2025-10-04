#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# File: scripts/run_cronos_machine.py
#
# Description:
# [DEFINITIVE "FIRST SPARK" TEST] This script runs the Cronos Machine in
# complete isolation to definitively prove that it can evolve a hardened
# champion that achieves a 'survived' outcome with a high positive fitness score.
#

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser
from cosmos.foundry.foundry import Foundry

CRONOS_GENOME_PATH = "data/genomes/cronos/cronos_v0.2.c"

# This configuration provides a static, NEWLINE-TERMINATED payload.
CRONOS_CONFIG = {
    "population_size": 10,
    "mutation_rate": 0.7,
    "generations": 5,
    "elitism_count": 2,
    "attack_payload": { 'payload_len': 50, 'char': 'A', 'terminator': '\n' }
}

def main():
    print("--- [CRONOS MACHINE] Starting definitive hardening test... ---")
    parser = CParser()
    try:
        cronos_ast = parser.parse_file(os.path.join(project_root, CRONOS_GENOME_PATH))
    except Exception as e:
        return print(f"FATAL: Could not parse initial genome. Error: {e}")
    
    foundry = Foundry(initial_cronos_ast=cronos_ast, config=CRONOS_CONFIG)
    champion = foundry.run_evolution()

    print("\n--- [CRONOS MACHINE] Run Complete ---")
    if champion and champion.get('genome'):
        print(f"Final Champion Fitness: {champion.get('fitness')}")
        final_code = parser.unparse(champion.get('genome'))
        print("\n--- Final Champion Code ---")
        print(final_code)
        if "fgets" in final_code and champion.get('fitness') > 0:
            print("\n[VERDICT] SUCCESS: The First Spark of Creation is confirmed.")
        else:
            print("\n[VERDICT] FAILURE: The system did not produce a viable, hardened champion.")

if __name__ == "__main__":
    main()
# scripts/run_foundry_v2.py
# [DEFINITIVE CRONOS-ONLY RUN] This script focuses ONLY on evolving Cronos
# against a static payload, returning to the last known stable architecture
# to confirm the final payload fix.

import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from cosmos.parser.parser import CParser
from cosmos.foundry.foundry import Foundry # Using the simplified static-Uranus foundry

CRONOS_GENOME_PATH = "data/genomes/cronos/cronos_v0.2.c"
FOUNDRY_CONFIG = {
    "population_size": 10, "mutation_rate": 0.5, "generations": 5, "elitism_count": 2
}

def main():
    print("--- Launching COSMOS-Ω Foundry v5 (Definitive Test) ---")
    parser = CParser()
    try:
        cronos_ast = parser.parse_file(os.path.join(project_root, CRONOS_GENOME_PATH))
    except Exception as e:
        return print(f"FATAL: Could not parse initial genome. Error: {e}")
    
    # We use the Foundry version that takes only a Cronos AST
    foundry = Foundry(initial_cronos_ast=cronos_ast, config=FOUNDRY_CONFIG)
    champion = foundry.run_evolution()
    
    print("\n--- Foundry Run Complete ---")
    if champion and champion.get('genome'):
        print(f"Final Champion Fitness: {champion.get('fitness')}")
        final_code = parser.unparse(champion.get('genome'))
        print("\n--- Final Champion Code ---")
        print(final_code)

if __name__ == "__main__":
    main()
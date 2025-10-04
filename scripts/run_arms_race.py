#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# File: scripts/run_arms_race.py
#
# Description:
# [DEFINITIVE STATE PROPAGATION FIX] This is the final, correct version.
# It fixes the critical state-reversion bug by ensuring that at the start
# of each Cronos turn, the orchestrator loads the CURRENT hardened champion
# from disk, rather than re-using the initial vulnerable AST. This enables
# true, cumulative co-evolution.
#

import os
import sys
import shutil

# --- Setup Project Root Path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser
from cosmos.foundry.foundry import Foundry
from cosmos.foundry.uranus_evolver import UranusEvolver

# --- Configuration ---
CRONOS_INITIAL_GENOME_PATH = "data/genomes/cronos/cronos_v0.2.c"
CRONOS_CHAMPION_PATH = "artifacts/cronos_champion.c"
ARMS_RACE_CYCLES = 5

CRONOS_CONFIG = { "population_size": 10, "mutation_rate": 0.8, "generations": 3, "elitism_count": 2 }
URANUS_CONFIG = { "population_size": 10, "mutation_rate": 0.8, "generations": 3 }

def main():
    """ The main orchestrator for the co-evolutionary arms race. """
    print("="*80)
    print("      ForgeX4 COSMOS-Ω: Co-Evolutionary Arms Race Initiated")
    print("="*80)

    parser = CParser()
    shutil.copy(os.path.join(project_root, CRONOS_INITIAL_GENOME_PATH), CRONOS_CHAMPION_PATH)
    print(f"Initial vulnerable champion staged at: {CRONOS_CHAMPION_PATH}")
    current_attack_payload = {'payload_len': 50, 'char': 'A', 'terminator': '\n'}

    # --- Main Co-Evolutionary Loop ---
    for cycle in range(1, ARMS_RACE_CYCLES + 1):
        print("\n" + "#"*30 + f" ARMS RACE CYCLE {cycle}/{ARMS_RACE_CYCLES} " + "#"*31)

        # === STAGE 1: URANUS'S TURN (Evolve the Attack) ===
        print("\n" + "-"*25 + " Activating Uranus Machine " + "-"*26)
        uranus_machine = UranusEvolver(CRONOS_CHAMPION_PATH, current_attack_payload, URANUS_CONFIG)
        current_attack_payload = uranus_machine.run_evolution()
        print(f"Uranus machine finished. New evolved attack payload: {current_attack_payload}")

        # === STAGE 2: CRONOS'S TURN (Evolve the Defense) ===
        print("\n" + "-"*25 + " Activating Cronos Machine " + "-"*27)
        
        # --- THE DEFINITIVE FIX ---
        # Load the CURRENT champion state from disk to ensure progress persists.
        print(f"Loading current champion from {CRONOS_CHAMPION_PATH} for next evolution...")
        try:
            current_champion_ast = parser.parse_file(CRONOS_CHAMPION_PATH)
        except Exception as e:
            print(f"FATAL: Could not parse current champion, halting: {e}")
            return
            
        CRONOS_CONFIG['attack_payload'] = current_attack_payload
        cronos_machine = Foundry(
            initial_cronos_ast=current_champion_ast, # Use the CURRENT champion
            config=CRONOS_CONFIG
        )
        new_cronos_champion = cronos_machine.run_evolution()

        # === STAGE 3: UPDATE THE BATTLEFIELD ===
        if new_cronos_champion and new_cronos_champion.get('genome'):
            print("\nUpdating battlefield with new Cronos champion...")
            champion_code = parser.unparse(new_cronos_champion['genome'])
            with open(CRONOS_CHAMPION_PATH, "w") as f:
                f.write("#include <stdio.h>\n#include <string.h>\n\n" + champion_code)
            print(f"SUCCESS: New hardened champion written to {CRONOS_CHAMPION_PATH}")
        else:
            print("WARNING: Cronos did not produce a viable new champion.")

    print("\n" + "="*80)
    print("                  Co-Evolutionary Arms Race Complete")
    print("="*80)

if __name__ == "__main__":
    main()
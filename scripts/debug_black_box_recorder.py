#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# File: scripts/debug_black_box_recorder.py
#
# Description:
# [URANUS VALIDATOR] This is a targeted diagnostic tool focused exclusively
# on the Uranus machine. It runs one full evolution of the attacker and
# provides a definitive report on the in-memory vs. returned state of the
# champion payload, validating the final persistence fix.
#

import os
import sys
import shutil

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# We only need UranusEvolver for this targeted test.
from cosmos.foundry.uranus_evolver import UranusEvolver

# --- Configuration for a single, definitive validation run ---
CRONOS_INITIAL_GENOME_PATH = "data/genomes/cronos/cronos_v0.2.c"
CRONOS_CHAMPION_PATH = "artifacts/cronos_champion.c"
URANUS_CONFIG = { "population_size": 10, "mutation_rate": 0.8, "generations": 3 }

def print_header(title):
    print("\n" + "="*25 + f" URANUS VALIDATOR: {title} " + "="*25)

def main():
    print("="*30 + " BLACK BOX RECORDER (URANUS FOCUS) " + "="*27)

    # Uranus needs a target to attack, so we stage the initial vulnerable defender.
    shutil.copy(os.path.join(project_root, CRONOS_INITIAL_GENOME_PATH), CRONOS_CHAMPION_PATH)
    initial_attack_payload = {'payload_len': 50, 'char': 'A', 'terminator': '\n'}

    # --- URANUS'S TURN (VALIDATE THE PERSISTENCE FIX) ---
    print_header("URANUS MACHINE ACTIVATED")
    # This calls the instrumented uranus_evolver.py, which has our in-memory probe
    uranus_machine = UranusEvolver(CRONOS_CHAMPION_PATH, initial_attack_payload, URANUS_CONFIG)
    returned_attack_payload = uranus_machine.run_evolution()

    print_header("POST-URANUS (RETURNED)")
    print("The orchestrator has RECEIVED the following payload from the Uranus machine:")
    print(f"--> {returned_attack_payload}")

    print("\n" + "="*80)
    print("URANUS VALIDATION COMPLETE.")
    print("Compare the 'IN-MEMORY' state from the probe with the 'RETURNED' state above.")
    print("="*80)

if __name__ == "__main__":
    main()
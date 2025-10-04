#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Date: 2025-09-29
#
# File: scripts/debug_state_inspector.py
#
# Description:
# [STATE INSPECTOR] A high-transparency debugging tool. This script runs a
# single, heavily instrumented arms race cycle to produce an unambiguous
# report of the system's state at every critical transition. Its purpose is
# to definitively identify the root cause of state corruption/reversion bugs.
#

import os
import sys
import shutil

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser
from cosmos.foundry.foundry import Foundry
from cosmos.foundry.uranus_evolver import UranusEvolver

# --- Configuration ---
CRONOS_INITIAL_GENOME_PATH = "data/genomes/cronos/cronos_v0.2.c"
CRONOS_CHAMPION_PATH = "artifacts/cronos_champion.c"
CRONOS_CONFIG = { "population_size": 10, "mutation_rate": 0.8, "generations": 3, "elitism_count": 2 }
URANUS_CONFIG = { "population_size": 10, "mutation_rate": 0.8, "generations": 3 }

def print_header(title):
    print("\n" + "="*25 + f" STATE INSPECTOR: {title} " + "="*25)

def main():
    parser = CParser()
    initial_cronos_ast = parser.parse_file(os.path.join(project_root, CRONOS_INITIAL_GENOME_PATH))
    shutil.copy(os.path.join(project_root, CRONOS_INITIAL_GENOME_PATH), CRONOS_CHAMPION_PATH)
    initial_attack_payload = {'payload_len': 50, 'char': 'A', 'terminator': '\n'}

    print_header("INITIAL STATE")
    print(f"Initial Attack Payload: {initial_attack_payload}")
    print("Initial Cronos Code (on disk):")
    with open(CRONOS_CHAMPION_PATH, 'r') as f:
        print(f.read())

    # --- URANUS'S TURN ---
    print_header("URANUS MACHINE ACTIVATED")
    uranus_machine = UranusEvolver(CRONOS_CHAMPION_PATH, initial_attack_payload, URANUS_CONFIG)
    returned_attack_payload = uranus_machine.run_evolution()

    print_header("POST-URANUS (RETURNED)")
    print("The orchestrator has RECEIVED the following payload from the Uranus machine:")
    print(f"--> {returned_attack_payload}")


    # --- CRONOS'S TURN ---
    print_header("CRONOS MACHINE ACTIVATED")
    CRONOS_CONFIG['attack_payload'] = returned_attack_payload
    cronos_machine = Foundry(initial_cronos_ast, CRONOS_CONFIG)
    returned_cronos_champion = cronos_machine.run_evolution()

    print_header("POST-CRONOS (RETURNED)")
    print("The orchestrator has RECEIVED the following champion object from the Cronos machine:")
    print(f"--> Fitness: {returned_cronos_champion.get('fitness')}")
    print("--> RETURNED Champion Code:")
    try:
        returned_code = parser.unparse(returned_cronos_champion['genome'])
        print(returned_code)
    except Exception as e:
        print(f"ERROR unparsing returned genome: {e}")


    # --- FINAL WRITE TO DISK ---
    print_header("FINAL STATE (ON-DISK)")
    print("Orchestrator is now writing the RETURNED champion code to disk...")
    try:
        final_code_to_save = "#include <stdio.h>\n#include <string.h>\n\n" + returned_code
        with open(CRONOS_CHAMPION_PATH, "w") as f:
            f.write(final_code_to_save)
        print(f"Write successful to {CRONOS_CHAMPION_PATH}")
    except Exception as e:
        print(f"ERROR during file write: {e}")

    print("\nVerifying final on-disk content by reading it back:")
    with open(CRONOS_CHAMPION_PATH, 'r') as f:
        print("--- ON-DISK CONTENT ---")
        print(f.read())
        print("--- END ON-DISK CONTENT ---")

    print("\n" + "="*71)
    print("STATE INSPECTION COMPLETE.")
    print("="*71)

if __name__ == "__main__":
    main()
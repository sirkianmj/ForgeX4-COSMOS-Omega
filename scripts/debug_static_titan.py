#
# ForgeX4 COSMOS-Ω
#
# File: scripts/debug_static_titan.py
# Date: 2025-09-27
#
# Description:
# [UPDATED] A targeted script to debug the now self-contained StaticAnalysisTitan.
#

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from cosmos.parser import parser
from cosmos.foundry.titans import StaticAnalysisTitan

CRONOS_GENOME_PATH = "data/genomes/cronos/cronos_v1.0.c"

def main():
    print("="*50)
    print("  Debugging Self-Contained StaticAnalysisTitan")
    print("="*50)

    titan = StaticAnalysisTitan()
    print("StaticAnalysisTitan Initialized.")

    print(f"Loading and parsing file: {CRONOS_GENOME_PATH}")
    try:
        code_ast = parser.parse_c_file_to_ast(CRONOS_GENOME_PATH)
        print("AST parsed successfully.")
    except Exception as e:
        print(f"Fatal Error: Could not parse source file. Details: {e}")
        sys.exit(1)
        
    print("\nRunning Titan's analysis method...")
    analysis_result = titan.analyze(code_ast)

    print("\n--- Raw Analysis Result ---")
    print(analysis_result)
    print("---------------------------\n")
    
    print("Debug script finished.")

if __name__ == "__main__":
    main()
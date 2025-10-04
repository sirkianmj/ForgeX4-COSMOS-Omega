#
# ForgeX4 COSMOS-Ω
#
# File: scripts/validate_performance_titan.py
# Date: 2025-09-27
#
# Description:
# A targeted validation script to prove the PerformanceTitan is working correctly.
# It compares the Titan's predicted CPU utilization for a known-low-workload
# genome against a known-high-workload genome.
#

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from cosmos.parser import parser
from cosmos.foundry.titans import PerformanceTitan

# --- Test Cases ---
LOW_WORKLOAD_PATH = "data/genomes/cronos/cronos_v1.0.c"
HIGH_WORKLOAD_PATH = "data/genomes/cronos/cronos_heavy_compute.c"

def main():
    print("="*60)
    print("  Definitive Validation Protocol for PerformanceTitan")
    print("="*60)

    # --- Step 1: Initialize the Titan ---
    titan = PerformanceTitan()
    # This will trigger the one-time lazy load of the v5.2 ensemble
    print("-" * 60)

    # --- Step 2: Analyze the Low-Workload Genome ---
    print(f"Analyzing LOW workload genome: {LOW_WORKLOAD_PATH}")
    try:
        low_workload_ast = parser.parse_c_file_to_ast(LOW_WORKLOAD_PATH)
        low_prediction_result = titan.predict(low_workload_ast)
        low_cpu_util = low_prediction_result.get('predicted_cpu_util', -1.0)
        print(f"  --> Predicted CPU Utilization: {low_cpu_util:.4f}")
    except Exception as e:
        print(f"  --> FAILED to analyze: {e}")
        low_cpu_util = -1.0
    print("-" * 60)

    # --- Step 3: Analyze the High-Workload Genome ---
    print(f"Analyzing HIGH workload genome: {HIGH_WORKLOAD_PATH}")
    try:
        high_workload_ast = parser.parse_c_file_to_ast(HIGH_WORKLOAD_PATH)
        high_prediction_result = titan.predict(high_workload_ast)
        high_cpu_util = high_prediction_result.get('predicted_cpu_util', -1.0)
        print(f"  --> Predicted CPU Utilization: {high_cpu_util:.4f}")
    except Exception as e:
        print(f"  --> FAILED to analyze: {e}")
        high_cpu_util = -1.0
    print("-" * 60)

    # --- Step 4: Conclusion ---
    print("\nValidation Conclusion:")
    if low_cpu_util != -1.0 and high_cpu_util != -1.0 and high_cpu_util > low_cpu_util:
        print("  [SUCCESS] The PerformanceTitan correctly predicted a higher")
        print(f"              CPU load for the heavy-compute genome ({high_cpu_util:.4f})")
        print(f"              than for the simple genome ({low_cpu_util:.4f}).")
        print("\n  The Titan is considered VALIDATED.")
    else:
        print("  [FAILURE] The PerformanceTitan did not perform as expected.")
        print("              Further debugging is required.")

    print("="*60)

if __name__ == "__main__":
    main()
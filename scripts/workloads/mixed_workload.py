# scripts/workloads/mixed_workload.py

import time
import math
import random

def run_mixed_workload(duration_seconds: int):
    """
    Simulates a mixed computation workload involving integer, floating-point,
    and memory-access operations.

    Args:
        duration_seconds: The approximate duration to run the workload.
    """
    print(f"[Workload:Mixed] Starting mixed-computation task for {duration_seconds} seconds.")
    start_time = time.time()

    # Pre-allocate a list to represent our memory component
    data = [random.random() for _ in range(100_000)]
    
    integer_result = 0
    float_result = 0.0

    try:
        while (time.time() - start_time) < duration_seconds:
            # 1. Integer-heavy operation (CRC32-like calculation)
            for i in range(0, len(data), 100):
                integer_result = (integer_result + int(data[i] * 1000)) & 0xFFFFFFFF

            # 2. Float-heavy operation (trigonometric functions)
            for i in range(0, len(data), 100):
                float_result += math.sin(data[i]) * math.cos(data[i])

            # 3. Memory-access heavy operation (list shuffling)
            # Shuffle a slice of the list to simulate pointer-chasing and cache misses
            slice_to_shuffle = data[1000:2000]
            random.shuffle(slice_to_shuffle)
            data[1000:2000] = slice_to_shuffle

    finally:
        del data
        print(f"[Workload:Mixed] Finished task. Final checksum (discarded): {integer_result}")


if __name__ == '__main__':
    # A simple test case
    run_mixed_workload(duration_seconds=10)
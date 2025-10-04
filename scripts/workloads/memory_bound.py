# scripts/workloads/memory_bound.py

import time
import random

def run_memory_bound_workload(duration_seconds: int):
    """
    Simulates a memory-bound workload by allocating and manipulating
    large lists in memory.

    Args:
        duration_seconds: The approximate duration to run the workload.
    """
    print(f"[Workload:Memory] Starting memory-bound task for {duration_seconds} seconds.")
    start_time = time.time()
    
    # We will work with a list of lists (a matrix-like structure)
    # The size is chosen to be significant but not crippling on a system with 16GB RAM.
    list_size = 5_000_000 # 5 million integers
    data_structure = []

    # Initial allocation
    print(f"[Workload:Memory] Allocating initial list of {list_size:,} integers...")
    data_structure.append([random.randint(0, 1000) for _ in range(list_size)])

    try:
        while (time.time() - start_time) < duration_seconds:
            # Operation 1: Create a new list and append
            new_list = [random.randint(0, 1000) for _ in range(list_size)]
            data_structure.append(new_list)

            # Operation 2: Sum the elements of a random list
            list_to_sum = random.choice(data_structure)
            _ = sum(list_to_sum) # The result is discarded, we only care about the operation

            # Operation 3: Remove a list to keep memory usage from growing indefinitely
            if len(data_structure) > 3:
                list_to_remove = data_structure.pop(0)
                del list_to_remove # Hint to the garbage collector
    
    finally:
        del data_structure # Clean up the reference
        print("[Workload:Memory] Finished task and cleaned up memory.")


if __name__ == '__main__':
    # A simple test case
    run_memory_bound_workload(duration_seconds=10)
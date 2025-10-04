# scripts/workloads/network_bound.py

import time
import requests
import concurrent.futures

# A list of reliable, high-availability public APIs to query.
# Using multiple endpoints makes the test more robust.
URLS = [
    "https://api.github.com",
    "https://www.google.com",
    "https://api.ipify.org?format=json",
    "https://httpbin.org/get",
]

def fetch_url(url):
    """Makes a single GET request and returns the status code."""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code
    except requests.RequestException:
        return None

def run_network_bound_workload(duration_seconds: int):
    """
    Simulates a network-bound workload by making concurrent HTTP requests
    to public endpoints.

    Args:
        duration_seconds: The approximate duration to run the workload.
    """
    print(f"[Workload:Network] Starting network-bound task for {duration_seconds} seconds.")
    start_time = time.time()
    
    # We use a ThreadPoolExecutor for I/O-bound tasks like network requests.
    # This allows us to make many requests concurrently.
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        while (time.time() - start_time) < duration_seconds:
            # Submit a batch of requests
            futures = [executor.submit(fetch_url, random.choice(URLS)) for _ in range(20)]
            
            # Wait for this batch to complete
            concurrent.futures.wait(futures)
            
            # A small delay to prevent overwhelming the network or getting rate-limited
            time.sleep(0.1)

    print("[Workload:Network] Finished task.")


if __name__ == '__main__':
    # A simple test case
    # Note: This test requires an active internet connection.
    print("Testing network workload... (Requires internet connection)")
    run_network_bound_workload(duration_seconds=10)
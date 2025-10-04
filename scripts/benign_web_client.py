# File: scripts/benign_web_client.py (v2.1 - "Swarm Aware")
import requests
import time
import sys

# Take the port number as a command-line argument
port = sys.argv[1] if len(sys.argv) > 1 else "8080"
url = f"http://127.0.0.1:{port}"

for i in range(20):
    try:
        requests.get(url, timeout=1)
    except requests.exceptions.RequestException:
        pass
    time.sleep(0.75)
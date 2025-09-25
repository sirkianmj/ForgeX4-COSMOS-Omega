#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: uranus_v0.1.py
# Date: 2024-05-24
#
# Description:
# The initial, simple attacker agent (fuzzer). Its goal is to provide
# the negative evolutionary pressure needed to drive Cronos's evolution.
# It does this by generating a simple buffer overflow payload and feeding it
# to the target binary.
#
import subprocess
import os

# --- Configuration ---
# The path to the compiled Gaia/Cronos binary.
# We assume it will be compiled in the project's root directory.
TARGET_BINARY_PATH = "./gaia_v0.1"

# A simple payload designed to overflow the 16-byte buffer in gaia_v0.1.c
# We send 32 'A's plus a newline character.
OVERFLOW_PAYLOAD = b"A" * 32 + b"\n"

def run_attack():
    """
    Executes a single attack run against the target binary.

    Returns:
        bool: True if the attack was successful (the program crashed), False otherwise.
    """
    print(f"Uranus: Attacking '{TARGET_BINARY_PATH}'...")
    try:
        # We will use the RISC-V user-mode emulator to run the target.
        # This is the same command we validated in Phase 0.
        command = ["qemu-riscv64-static", TARGET_BINARY_PATH]

        # Start the process. We pipe stdin to send our payload.
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Send the payload and wait for the process to terminate.
        # A timeout is used to prevent hangs.
        stdout, stderr = process.communicate(OVERFLOW_PAYLOAD, timeout=5)

        # A non-zero return code indicates a crash (e.g., segmentation fault).
        if process.returncode != 0 and process.returncode < 0: # Negative codes are from signals
            print(f"Uranus: SUCCESS! Target crashed with signal: {abs(process.returncode)}.")
            return True
        else:
            print("Uranus: FAILURE. Target did not crash.")
            return False

    except FileNotFoundError:
        print(f"Uranus: ERROR! Target binary '{TARGET_BINARY_PATH}' not found.")
        print("Please compile gaia_v0.1.c and cronos_v0.1.c first.")
        return False
    except subprocess.TimeoutExpired:
        print("Uranus: FAILURE. Target timed out.")
        process.kill()
        return False
    except Exception as e:
        print(f"Uranus: An unexpected error occurred: {e}")
        return False

if __name__ == '__main__':
    # This script serves as the fitness evaluation function for now.
    # We will call this from the main foundry loop later.
    run_attack()
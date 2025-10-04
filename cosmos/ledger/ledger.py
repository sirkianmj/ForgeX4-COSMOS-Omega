import json
import hashlib
from datetime import datetime
from pathlib import Path
import os
import binascii
from rich import print

# [DEFINITIVE - V4.2 "OMEGA LEDGER - GUI COMPATIBLE" - FINAL VERSION]
# This version maintains the full blockchain-like structure of V4.1.
#
# BUG FIX:
# - Renamed the internal list from `self.chain` to `self.events`.
# - This makes the Ledger's state readable by the Flask GUI thread,
#   resolving the 'AttributeError' without removing any features.

class Ledger:
    """
    Creates a cryptographically-chained, auditable log of an evolutionary run,
    structured like a simple blockchain.
    """
    def __init__(self, output_dir: str = "artifacts/logs"):
        """Initializes the Ledger, the Run ID, and the cryptographic chain."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.run_id = binascii.hexlify(os.urandom(8)).decode()
        run_timestamp = self._get_timestamp(time_format="%Y%m%d_%H%M%S")
        self.ledger_path = self.output_dir / f"ledger_{run_timestamp}_{self.run_id}.json"
        
        # --- FIX: Renamed `self.chain` to `self.events` for GUI compatibility ---
        self.events = []
        
        self.genesis_hash = '0' * 64
        self.previous_hash = self.genesis_hash
        
        print(f"Ledger initialized. Run ID: {self.run_id}")
        print(f"  - Run log will be saved to: {self.ledger_path}")
        
        self.record_event(block_height=0, event_type="GENESIS", details={"run_id": self.run_id, "detail": "Cryptographic chain initiated."})

    def _get_timestamp(self, time_format: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> str:
        """Generates a UTC timestamp in a standardized format."""
        return datetime.utcnow().strftime(time_format)

    def _calculate_block_hash(self, block_data: dict) -> str:
        """Calculates the SHA-256 hash for a block."""
        block_string = json.dumps(block_data, sort_keys=True, default=str).encode('utf-8')
        return hashlib.sha256(block_string).hexdigest()

    def record_event(self, block_height: int, event_type: str, details: dict):
        """
        Records a new event "block" and links it to the cryptographic chain.
        """
        block = {
            "run_id": self.run_id,
            "block_height": block_height,
            "nonce": binascii.hexlify(os.urandom(4)).decode(),
            "timestamp": self._get_timestamp(),
            "event_type": event_type,
            "details": details,
            "previous_hash": self.previous_hash
        }

        current_hash = self._calculate_block_hash(block)
        block["block_hash"] = current_hash
        
        # --- FIX: Appending to `self.events` instead of `self.chain` ---
        self.events.append(block)
        
        self.previous_hash = current_hash

    def save(self):
        """Saves the complete blockchain of events to a JSON file."""
        try:
            # --- FIX: Dumping `self.events` instead of `self.chain` ---
            with open(self.ledger_path, 'w') as f:
                json.dump(self.events, f, indent=2, default=str)
            print(f"Successfully saved ledger with {len(self.events)} blocks to {self.ledger_path}")
        except (IOError, TypeError) as e:
            print(f"[bold red]Error: Could not write or serialize ledger. Reason: {e}[/bold red]")
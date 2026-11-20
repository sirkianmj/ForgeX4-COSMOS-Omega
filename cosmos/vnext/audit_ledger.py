import copy
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class AuditLedger:
    """Tamper-evident SHA-256 hash-chained ledger with immutable deepcopied events."""

    def __init__(self, out_dir: Path, run_name: str = "vnext_run"):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = uuid.uuid4().hex[:16]
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.path = self.out_dir / f"ledger_{run_name}_{ts}_{self.run_id}.json"
        self.events: List[Dict[str, Any]] = []
        self._prev_hash = "0" * 64

    def record(self, event_type: str, data: Dict[str, Any]):
        entry = {
            "seq": len(self.events),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event_type": event_type,
            "data": copy.deepcopy(data),
            "prev_hash": self._prev_hash,
        }
        digest = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()
        entry["hash"] = digest
        self._prev_hash = digest
        self.events.append(entry)

    def save(self) -> Path:
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"run_id": self.run_id, "events": self.events}, f, indent=2)
        os.replace(tmp, self.path)
        return self.path

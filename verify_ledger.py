#!/usr/bin/env python3
"""
verify_ledger.py — Honest cryptographic verification of COSMOS-Omega SHA-256 ledgers.
"""

import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

EXPECTED_PATH = (
    "artifacts/vnext_logs/ledger_journal115_20261121_103606_f10dab7dbf054b8d.json"
)


def hash_strict(ev):
    unhashed = {k: v for k, v in ev.items() if k != "hash"}
    return hashlib.sha256(json.dumps(unhashed, sort_keys=True).encode("utf-8")).hexdigest()


def hash_pre_tag_lenient(ev):
    """Recompute digest excluding post-record split/seed reporting tags."""
    e = copy.deepcopy(ev)
    e.pop("hash", None)
    if isinstance(e.get("data"), dict):
        e["data"].pop("split", None)
        e["data"].pop("seed", None)
    return hashlib.sha256(json.dumps(e, sort_keys=True).encode("utf-8")).hexdigest()


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else EXPECTED_PATH)
    print(f"Verifying ledger: {path}")
    if not path.exists():
        sys.exit(f"File not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    events = data["events"]
    print(f"Total events: {len(events)}")
    print(f"Sequence range: {events[0]['seq']} -> {events[-1]['seq']}")
    print(f"Terminal block hash: {events[-1]['hash']}\n")

    archetypes, splits, seeds = Counter(), Counter(), Counter()
    for ev in events:
        d = ev.get("data", {})
        archetypes[d.get("archetype", "<none>")] += 1
        splits[d.get("split", "<none>")] += 1
        seeds[d.get("seed", "<none>")] += 1

    print("=== ARCHETYPE DISTRIBUTION ===")
    for k, v in archetypes.most_common():
        print(f"  {k:12s} {v}")

    print("\n=== SPLIT DISTRIBUTION ===")
    for k, v in splits.most_common():
        print(f"  {k:20s} {v}")

    print("\n=== SEED DISTRIBUTION ===")
    for k, v in sorted(seeds.items(), key=lambda x: str(x[0])):
        print(f"  Seed {k!s:<8s} {v}")

    prev = "0" * 64
    chain_ok = 0
    strict_ok = 0
    lenient_ok = 0
    for ev in events:
        if ev.get("prev_hash") == prev:
            chain_ok += 1
        if hash_strict(ev) == ev["hash"]:
            strict_ok += 1
        if hash_pre_tag_lenient(ev) == ev["hash"]:
            lenient_ok += 1
        prev = ev["hash"]

    print("\n=== CRYPTOGRAPHIC INTEGRITY ===")
    print(f"  Valid consecutive prev_hash links:           {chain_ok}/{len(events)}")
    print(f"  Strict payload SHA-256 (all fields):         {strict_ok}/{len(events)}")
    print(f"  Runtime pre-tag SHA-256 (ex split/seed):     {lenient_ok}/{len(events)}")

    sjp = sum(
        1 for ev in events
        if ev["data"]["cosmos_omega"]["benign_pass_rate"] == 1.0
        and ev["data"]["cosmos_omega"]["attack_block_rate"] == 1.0
        and ev["data"]["cosmos_omega"]["z3_verified"] is True
    )
    print("\n=== BENCHMARK EVALUATION ===")
    print(f"  Strict Joint Pass: {sjp}/{len(events)} ({sjp/len(events)*100:.2f}%)")


if __name__ == "__main__":
    main()

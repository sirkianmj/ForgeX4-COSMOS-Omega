#!/usr/bin/env python3
"""
scripts/verify_paper_metrics.py — Independently recalculates all tables,
threat-class histograms, and Mann-Whitney U p-values directly from the raw JSON ledger.
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_LEDGER = Path("artifacts/vnext_logs/ledger_journal115_20261121_103606_f10dab7dbf054b8d.json")
LEDGER_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LEDGER


def mann_whitney_u_pvalue(xs, ys) -> float:
    nx, ny = len(xs), len(ys)
    if nx == 0 or ny == 0:
        return 1.0
    combined = [(v, 0) for v in xs] + [(v, 1) for v in ys]
    combined.sort(key=lambda t: t[0])
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j + 1 < len(combined) and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    r1 = sum(ranks[idx] for idx, (_, grp) in enumerate(combined) if grp == 0)
    u1 = r1 - nx * (nx + 1) / 2.0
    mean_u = nx * ny / 2.0
    std_u = math.sqrt(nx * ny * (nx + ny + 1) / 12.0)
    if std_u == 0:
        return 1.0
    z = abs(u1 - mean_u) / std_u
    return math.erfc(z / math.sqrt(2.0))


def main():
    print(f"Loading raw ledger: {LEDGER_PATH}")
    data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    events = data["events"]
    print(f"Auditing {len(events)} events across {len(set(e['data']['target_id'] for e in events))} distinct targets.\n")

    print("=" * 68)
    print("1. ALL NON-PASSING EVENTS (DYNAMICALLY SCANNED)")
    print("=" * 68)
    gaps = [
        ev for ev in events
        if not (
            ev["data"]["cosmos_omega"]["benign_pass_rate"] == 1.0
            and ev["data"]["cosmos_omega"]["attack_block_rate"] == 1.0
            and ev["data"]["cosmos_omega"]["z3_verified"] is True
        )
    ]
    print(f"Found {len(gaps)} non-passing events out of {len(events)}:\n")
    for ev in gaps:
        d = ev["data"]
        co = d["cosmos_omega"]
        print(f"Event seq {ev['seq']:3d} ({d['target_id']}, seed {d.get('seed')}, split {d.get('split')}):")
        print(f"  Benign={co['benign_pass_rate']} | Block={co['attack_block_rate']} | Z3={co['z3_verified']}")
        print(f"  Policy wall={co['policy']['wall_ms']} ms | CPU budget={co['policy']['max_cpu_ms_budget']} ms | RSS budget={co['policy']['max_rss_kb_budget']} KB")
        for ad in co["attack_details"]:
            if not ad["blocked"]:
                cpu_str = f"{ad['cpu_ms']} ms" if "cpu_ms" in ad else "<missing>"
                print(f"  Unblocked Probe: {ad['probe']} ({ad['threat_class']}) -> outcome={ad['outcome']}, wall_ms={ad['wall_ms']} ms, cpu_ms={cpu_str}")
        print()

    print("=" * 68)
    print("2. ZERO-SHOT LEAVE-23-TARGETS-OUT (LOTO) TRANSFER IN ISOLATION")
    print("=" * 68)
    splits = defaultdict(list)
    for ev in events:
        sp = ev["data"].get("split", "unknown")
        co = ev["data"]["cosmos_omega"]
        jp = (co["benign_pass_rate"] == 1.0 and co["attack_block_rate"] == 1.0 and co["z3_verified"] is True)
        splits[sp].append(jp)

    for sp in sorted(splits.keys()):
        p = sum(splits[sp])
        t = len(splits[sp])
        print(f"  Partition '{sp:14s}': {p}/{t} strict joint pass = {p/t*100:.2f}%")

    print("\n" + "=" * 68)
    print("3. THREAT-CLASS CONTAINMENT HISTOGRAM (740 TOTAL PROBES)")
    print("=" * 68)
    tc_stats = defaultdict(lambda: {"total": 0, "blocked": 0})
    for ev in events:
        for ad in ev["data"]["cosmos_omega"]["attack_details"]:
            tc = ad["threat_class"]
            tc_stats[tc]["total"] += 1
            if ad["blocked"]:
                tc_stats[tc]["blocked"] += 1

    tot_p = sum(s["total"] for s in tc_stats.values())
    tot_b = sum(s["blocked"] for s in tc_stats.values())
    print(f"  {'Threat Class':<20} {'Probes':<8} {'Blocked':<8} {'Containment'}")
    print("  " + "-" * 48)
    for tc in sorted(tc_stats.keys()):
        t = tc_stats[tc]["total"]
        b = tc_stats[tc]["blocked"]
        print(f"  {tc:<20} {t:<8} {b:<8} {b/t*100:.1f}%")
    print("  " + "-" * 48)
    print(f"  {'COMPOSITE':<20} {tot_p:<8} {tot_b:<8} {tot_b/tot_p*100:.2f}%\n")

    print("=" * 68)
    print("4. MANN-WHITNEY U STATISTICAL SIGNIFICANCE (575 RUNS)")
    print("=" * 68)
    c_joint, q_joint, r_joint = [], [], []
    c_fit, r_fit = [], []
    for ev in events:
        d = ev["data"]
        co = d["cosmos_omega"]
        q2 = d["baseline_quantile_2float"]
        rs = d["baseline_random_search"]
        c_joint.append(1.0 if (co["benign_pass_rate"] == 1.0 and co["attack_block_rate"] == 1.0 and co["z3_verified"] is True) else 0.0)
        q_joint.append(1.0 if (q2["benign_pass_rate"] == 1.0 and q2["attack_block_rate"] == 1.0) else 0.0)
        r_joint.append(1.0 if (rs["benign_pass_rate"] == 1.0 and rs["attack_block_rate"] == 1.0) else 0.0)
        c_fit.append(co["fitness"])
        r_fit.append(rs["fitness"])

    print(f"  COSMOS-Omega vs 2-Float Sentinel (Joint Pass):  p = {mann_whitney_u_pvalue(c_joint, q_joint):.3e}")
    print(f"  COSMOS-Omega vs Random Search    (Joint Pass):  p = {mann_whitney_u_pvalue(c_joint, r_joint):.3e}")
    print(f"  COSMOS-Omega vs Random Search    (Fitness):     p = {mann_whitney_u_pvalue(c_fit, r_fit):.3e}")


if __name__ == "__main__":
    main()

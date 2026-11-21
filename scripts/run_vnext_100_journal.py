import argparse
import csv
import math
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.vnext import AuditLedger, GeneralistFoundry, SandboxClient, load_catalog
from cosmos.vnext.foundry import CrossTargetDigitalTwin


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


def _eval_one(foundry, target, pop, gens, pace_ms, split_name):
    r = foundry.synthesize(target, pop, gens, True, split=split_name)
    r["split"] = split_name
    if pace_ms > 0:
        time.sleep(pace_ms / 1000.0)
    return r


def run_seed(targets, client, ledger, seed: int, workers: int, pop: int, gens: int, pace_ms: int):
    twin = CrossTargetDigitalTwin()
    foundry = GeneralistFoundry(client=client, ledger=ledger, seed=seed, shared_twin=twin)

    train_targets = [t for i, t in enumerate(targets) if i % 5 != 4]
    test_targets = [t for i, t in enumerate(targets) if i % 5 == 4]

    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_eval_one, foundry, t, pop, gens, pace_ms, "train_92") for t in train_targets]
        for fut in as_completed(futs):
            results.append(fut.result())

    twin.fit_now()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_eval_one, foundry, t, pop, gens, pace_ms, "unseen_loto_23") for t in test_targets]
        for fut in as_completed(futs):
            results.append(fut.result())

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--pace-ms", type=int, default=15)
    ap.add_argument("--pop", type=int, default=8)
    ap.add_argument("--gens", type=int, default=4)
    args = ap.parse_args()

    console = Console()
    console.rule("[bold cyan]COSMOS-Ω vNext: 115-Target Thermal-Safe Journal Benchmark[/bold cyan]")

    client = SandboxClient()
    client.ensure_running()
    out_dir = PROJECT_ROOT / "artifacts" / "vnext_logs"
    ledger = AuditLedger(out_dir, run_name="journal115")

    t1 = load_catalog(PROJECT_ROOT / "targets" / "catalog" / "batch1_50.yaml", PROJECT_ROOT)
    t2 = load_catalog(PROJECT_ROOT / "targets" / "catalog" / "batch2_50.yaml", PROJECT_ROOT)
    t3 = load_catalog(PROJECT_ROOT / "targets" / "catalog" / "complex_apps_15.yaml", PROJECT_ROOT)
    targets = t1 + t2 + t3
    console.print(f"Loaded [bold]{len(targets)}[/bold] distinct targets (workers={args.workers}, pace={args.pace_ms}ms).")

    all_runs = []
    t_start = time.time()
    for s_idx in range(args.seeds):
        seed = 100 + s_idx
        t0 = time.time()
        res = run_seed(targets, client, ledger, seed, args.workers, args.pop, args.gens, args.pace_ms)
        c_joint = sum(
            1 for r in res
            if r["cosmos_omega"]["benign_pass_rate"] == 1.0
            and r["cosmos_omega"]["attack_block_rate"] == 1.0
            and r["cosmos_omega"]["z3_verified"]
        )
        q_joint = sum(
            1 for r in res
            if r["baseline_quantile_2float"]["benign_pass_rate"] == 1.0
            and r["baseline_quantile_2float"]["attack_block_rate"] == 1.0
        )
        r_joint = sum(
            1 for r in res
            if r["baseline_random_search"]["benign_pass_rate"] == 1.0
            and r["baseline_random_search"]["attack_block_rate"] == 1.0
        )
        loto_sub = [r for r in res if r["split"] == "unseen_loto_23"]
        loto_joint = sum(
            1 for r in loto_sub
            if r["cosmos_omega"]["benign_pass_rate"] == 1.0
            and r["cosmos_omega"]["attack_block_rate"] == 1.0
            and r["cosmos_omega"]["z3_verified"]
        )
        console.print(
            f"Seed {seed} ({time.time()-t0:.1f}s) | Strict Joint Pass: "
            f"[green]COSMOS={c_joint}/{len(targets)}[/green] | "
            f"2-Float={q_joint}/{len(targets)} | Random={r_joint}/{len(targets)} | "
            f"Unseen LOTO={loto_joint}/{len(loto_sub)}"
        )
        for r in res:
            r["seed"] = seed
        all_runs.extend(res)

    tc_stats = defaultdict(lambda: {"total": 0, "cosmos_blocked": 0})
    for r in all_runs:
        for ad in r["cosmos_omega"].get("attack_details", []):
            tc = ad["threat_class"]
            tc_stats[tc]["total"] += 1
            if ad["blocked"]:
                tc_stats[tc]["cosmos_blocked"] += 1

    arch_table = Table(title=f"COSMOS-Ω 115-Target Evaluation ({args.seeds} Seeds = {len(all_runs)} Runs, {time.time()-t_start:.1f}s)")
    arch_table.add_column("Archetype")
    arch_table.add_column("Runs", justify="right")
    arch_table.add_column("COSMOS Ben", justify="right")
    arch_table.add_column("COSMOS Blk", justify="right")
    arch_table.add_column("2-Float Blk", justify="right")
    arch_table.add_column("COSMOS Joint%", justify="right")
    arch_table.add_column("2-Float Joint%", justify="right")
    arch_table.add_column("Rand Joint%", justify="right")

    for arch in ["parser", "cli", "daemon", "agent"]:
        sub = [r for r in all_runs if r["archetype"] == arch]
        m = len(sub)
        cb = sum(r["cosmos_omega"]["benign_pass_rate"] for r in sub) / m * 100
        ck = sum(r["cosmos_omega"]["attack_block_rate"] for r in sub) / m * 100
        qk = sum(r["baseline_quantile_2float"]["attack_block_rate"] for r in sub) / m * 100
        cj = sum(1 for r in sub if r["cosmos_omega"]["benign_pass_rate"] == 1.0 and r["cosmos_omega"]["attack_block_rate"] == 1.0 and r["cosmos_omega"]["z3_verified"]) / m * 100
        qj = sum(1 for r in sub if r["baseline_quantile_2float"]["benign_pass_rate"] == 1.0 and r["baseline_quantile_2float"]["attack_block_rate"] == 1.0) / m * 100
        rj = sum(1 for r in sub if r["baseline_random_search"]["benign_pass_rate"] == 1.0 and r["baseline_random_search"]["attack_block_rate"] == 1.0) / m * 100
        arch_table.add_row(arch, str(m), f"{cb:.1f}%", f"{ck:.1f}%", f"{qk:.1f}%", f"{cj:.1f}%", f"{qj:.1f}%", f"{rj:.1f}%")

    console.print(arch_table)

    tc_table = Table(title="Containment Rate by Threat Class (115 Targets)")
    tc_table.add_column("Threat Class", style="cyan")
    tc_table.add_column("Probes", justify="right")
    tc_table.add_column("Contained", justify="right")
    tc_table.add_column("Rate", justify="right")
    for tc, st in sorted(tc_stats.items()):
        rate = st["cosmos_blocked"] / max(1, st["total"]) * 100
        tc_table.add_row(tc, str(st["total"]), str(st["cosmos_blocked"]), f"{rate:.1f}%")
    console.print(tc_table)

    c_scores = [1.0 if (r["cosmos_omega"]["benign_pass_rate"] == 1.0 and r["cosmos_omega"]["attack_block_rate"] == 1.0 and r["cosmos_omega"]["z3_verified"]) else 0.0 for r in all_runs]
    q_scores = [1.0 if (r["baseline_quantile_2float"]["benign_pass_rate"] == 1.0 and r["baseline_quantile_2float"]["attack_block_rate"] == 1.0) else 0.0 for r in all_runs]
    r_scores = [1.0 if (r["baseline_random_search"]["benign_pass_rate"] == 1.0 and r["baseline_random_search"]["attack_block_rate"] == 1.0) else 0.0 for r in all_runs]
    c_fit = [r["cosmos_omega"]["fitness"] for r in all_runs]
    r_fit = [r["baseline_random_search"]["fitness"] for r in all_runs]

    console.print(f"\n[bold]Mann-Whitney U (Joint Pass) vs 2-Float Sentinel:[/bold] p = {mann_whitney_u_pvalue(c_scores, q_scores):.3e}")
    console.print(f"[bold]Mann-Whitney U (Joint Pass) vs Random Search:[/bold]    p = {mann_whitney_u_pvalue(c_scores, r_scores):.3e}")
    console.print(f"[bold]Mann-Whitney U (Fitness)    vs Random Search:[/bold]    p = {mann_whitney_u_pvalue(c_fit, r_fit):.3e}")

    csv_path = out_dir / "results_115.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed", "split", "target_id", "archetype", "z3", "cosmos_benign", "cosmos_block", "priv_surface", "wall_ms", "q2_benign", "q2_block", "rand_benign", "rand_block"])
        for r in all_runs:
            co = r["cosmos_omega"]
            q2 = r["baseline_quantile_2float"]
            rs = r["baseline_random_search"]
            w.writerow([r["seed"], r["split"], r["target_id"], r["archetype"], co["z3_verified"], co["benign_pass_rate"], co["attack_block_rate"], co["privilege_surface"], co["mean_benign_wall_ms"], q2["benign_pass_rate"], q2["attack_block_rate"], rs["benign_pass_rate"], rs["attack_block_rate"]])

    tex_path = out_dir / "paper_tables_115.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\centering\n\\caption{COSMOS-$\\Omega$ 115-Target Generalization Benchmark}\n")
        f.write("\\begin{tabular}{lrrrrr}\n\\hline\n")
        f.write("Archetype & Runs & COSMOS Ben & COSMOS Blk & 2-Float Blk & Joint Pass \\\\\n\\hline\n")
        for arch in ["parser", "cli", "daemon", "agent"]:
            sub = [r for r in all_runs if r["archetype"] == arch]
            m = len(sub)
            cb = sum(r["cosmos_omega"]["benign_pass_rate"] for r in sub) / m * 100
            ck = sum(r["cosmos_omega"]["attack_block_rate"] for r in sub) / m * 100
            qk = sum(r["baseline_quantile_2float"]["attack_block_rate"] for r in sub) / m * 100
            cj = sum(1 for r in sub if r["cosmos_omega"]["benign_pass_rate"] == 1.0 and r["cosmos_omega"]["attack_block_rate"] == 1.0 and r["cosmos_omega"]["z3_verified"]) / m * 100
            f.write(f"{arch} & {m} & {cb:.1f}\\% & {ck:.1f}\\% & {qk:.1f}\\% & {cj:.1f}\\% \\\\\n")
        f.write("\\hline\n\\end{tabular}\n\\end{table}\n")

    ledger_path = ledger.save()
    console.print(f"CSV:    [cyan]{csv_path}[/cyan]")
    console.print(f"LaTeX:  [cyan]{tex_path}[/cyan]")
    console.print(f"Ledger: [cyan]{ledger_path}[/cyan]")


if __name__ == "__main__":
    main()

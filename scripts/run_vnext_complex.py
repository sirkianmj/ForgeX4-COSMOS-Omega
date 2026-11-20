import argparse
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.vnext import AuditLedger, GeneralistFoundry, SandboxClient, load_catalog
from cosmos.vnext.foundry import CrossTargetDigitalTwin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="targets/catalog/complex_apps_15.yaml")
    ap.add_argument("--pace-ms", type=int, default=25)
    ap.add_argument("--pop", type=int, default=8)
    ap.add_argument("--gens", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    console = Console()
    console.rule(f"[bold cyan]COSMOS-Ω Complex Apps Benchmark (Thermal-Safe 1-Worker, {args.catalog})[/bold cyan]")

    client = SandboxClient()
    client.ensure_running()
    ledger = AuditLedger(PROJECT_ROOT / "artifacts" / "vnext_logs", run_name="complex15")
    twin = CrossTargetDigitalTwin()
    foundry = GeneralistFoundry(client=client, ledger=ledger, seed=args.seed, shared_twin=twin)

    targets = load_catalog(PROJECT_ROOT / args.catalog, PROJECT_ROOT)
    table = Table(title=f"COSMOS-Ω Complex & Multi-Process Suite ({len(targets)} Targets)")
    table.add_column("Target", style="cyan")
    table.add_column("Type")
    table.add_column("Z3")
    table.add_column("COSMOS Ben/Blk", justify="right")
    table.add_column("2-Float Ben/Blk", justify="right")
    table.add_column("Rand Ben/Blk", justify="right")
    table.add_column("Priv", justify="right")

    results = []
    t0 = time.time()
    for idx, t in enumerate(targets, 1):
        res = foundry.synthesize(t, pop_size=args.pop, generations=args.gens, use_twin=True)
        results.append(res)
        co = res["cosmos_omega"]
        q2 = res["baseline_quantile_2float"]
        rs = res["baseline_random_search"]
        console.print(
            f"[{idx:02d}/{len(targets):02d}] [cyan]{t.id:<28}[/cyan] | "
            f"COSMOS={co['benign_pass_rate']*100:.0f}%/{co['attack_block_rate']*100:.0f}% | "
            f"2-Float={q2['benign_pass_rate']*100:.0f}%/{q2['attack_block_rate']*100:.0f}% | "
            f"Rand={rs['benign_pass_rate']*100:.0f}%/{rs['attack_block_rate']*100:.0f}%"
        )
        table.add_row(
            t.id,
            t.archetype,
            "PASS" if co["z3_verified"] else "FAIL",
            f"{co['benign_pass_rate']*100:.0f}% / {co['attack_block_rate']*100:.0f}%",
            f"{q2['benign_pass_rate']*100:.0f}% / {q2['attack_block_rate']*100:.0f}%",
            f"{rs['benign_pass_rate']*100:.0f}% / {rs['attack_block_rate']*100:.0f}%",
            f"{co['privilege_surface']:.2f}",
        )
        if args.pace_ms > 0:
            time.sleep(args.pace_ms / 1000.0)

    console.print(table)
    lp = ledger.save()
    n = len(results)
    c_joint = sum(1 for r in results if r["cosmos_omega"]["benign_pass_rate"] == 1.0 and r["cosmos_omega"]["attack_block_rate"] == 1.0 and r["cosmos_omega"]["z3_verified"])
    q_joint = sum(1 for r in results if r["baseline_quantile_2float"]["benign_pass_rate"] == 1.0 and r["baseline_quantile_2float"]["attack_block_rate"] == 1.0)
    r_joint = sum(1 for r in results if r["baseline_random_search"]["benign_pass_rate"] == 1.0 and r["baseline_random_search"]["attack_block_rate"] == 1.0)
    console.print(f"\nDone in {time.time()-t0:.1f}s | Strict Joint Pass: [green]COSMOS={c_joint}/{n}[/green] | 2-Float={q_joint}/{n} | Random={r_joint}/{n}")
    console.print(f"Ledger: [cyan]{lp}[/cyan]")


if __name__ == "__main__":
    main()

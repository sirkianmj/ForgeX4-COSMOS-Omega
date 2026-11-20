import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.vnext import AuditLedger, GeneralistFoundry, SandboxClient, load_catalog
from cosmos.vnext.foundry import CrossTargetDigitalTwin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="targets/catalog/batch1_50.yaml")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--pop", type=int, default=8)
    ap.add_argument("--gens", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    console = Console()
    console.rule(f"[bold cyan]COSMOS-Ω vNext Batch Runner ({args.catalog})[/bold cyan]")

    client = SandboxClient()
    client.ensure_running()
    ledger = AuditLedger(PROJECT_ROOT / "artifacts" / "vnext_logs", run_name=Path(args.catalog).stem)
    shared_twin = CrossTargetDigitalTwin()
    foundry = GeneralistFoundry(client=client, ledger=ledger, seed=args.seed, shared_twin=shared_twin)

    targets = load_catalog(PROJECT_ROOT / args.catalog, PROJECT_ROOT)
    t_all = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {
            pool.submit(foundry.synthesize, t, args.pop, args.gens, True): t
            for t in targets
        }
        done_cnt = 0
        for fut in as_completed(futs):
            t = futs[fut]
            done_cnt += 1
            res = fut.result()
            results.append(res)
            co = res["cosmos_omega"]
            q2 = res["baseline_quantile_2float"]
            rs = res["baseline_random_search"]
            console.print(
                f"[{done_cnt:02d}/{len(targets):02d}] [cyan]{t.id:<24}[/cyan] ({t.archetype:<6}) | "
                f"COSMOS={co['benign_pass_rate']*100:.0f}%/{co['attack_block_rate']*100:.0f}% | "
                f"2-Float={q2['benign_pass_rate']*100:.0f}%/{q2['attack_block_rate']*100:.0f}% | "
                f"Rand={rs['benign_pass_rate']*100:.0f}%/{rs['attack_block_rate']*100:.0f}%"
            )

    order = {t.id: i for i, t in enumerate(targets)}
    results.sort(key=lambda r: order[r["target_id"]])

    table = Table(title=f"COSMOS-Ω Summary ({len(results)} Targets, {time.time() - t_all:.1f}s)")
    table.add_column("Target", style="cyan")
    table.add_column("Type")
    table.add_column("Z3")
    table.add_column("COSMOS Ben/Blk", justify="right")
    table.add_column("2-Float Ben/Blk", justify="right")
    table.add_column("Random Ben/Blk", justify="right")
    table.add_column("Priv", justify="right")

    for r in results:
        co = r["cosmos_omega"]
        q2 = r["baseline_quantile_2float"]
        rs = r["baseline_random_search"]
        table.add_row(
            r["target_id"],
            r["archetype"],
            "PASS" if co["z3_verified"] else "FAIL",
            f"{co['benign_pass_rate']*100:.0f}% / {co['attack_block_rate']*100:.0f}%",
            f"{q2['benign_pass_rate']*100:.0f}% / {q2['attack_block_rate']*100:.0f}%",
            f"{rs['benign_pass_rate']*100:.0f}% / {rs['attack_block_rate']*100:.0f}%",
            f"{co['privilege_surface']:.2f}",
        )

    console.print(table)
    ledger_path = ledger.save()
    n = len(results)
    c_ben = sum(r["cosmos_omega"]["benign_pass_rate"] for r in results) / n
    c_blk = sum(r["cosmos_omega"]["attack_block_rate"] for r in results) / n
    c_joint = sum(1 for r in results if r["cosmos_omega"]["benign_pass_rate"] == 1.0 and r["cosmos_omega"]["attack_block_rate"] == 1.0 and r["cosmos_omega"]["z3_verified"])
    q_blk = sum(r["baseline_quantile_2float"]["attack_block_rate"] for r in results) / n
    q_joint = sum(1 for r in results if r["baseline_quantile_2float"]["benign_pass_rate"] == 1.0 and r["baseline_quantile_2float"]["attack_block_rate"] == 1.0)
    r_joint = sum(1 for r in results if r["baseline_random_search"]["benign_pass_rate"] == 1.0 and r["baseline_random_search"]["attack_block_rate"] == 1.0)

    console.print(f"\n[bold green]COSMOS-Ω:[/bold green] Mean Benign={c_ben*100:.1f}% | Mean Block={c_blk*100:.1f}% | Strict Joint Pass (100% Ben + 100% Blk + Z3)={c_joint}/{n}")
    console.print(f"[bold yellow]2-Float Sentinel:[/bold yellow] Mean Block={q_blk*100:.1f}% | Strict Joint Pass={q_joint}/{n}")
    console.print(f"[bold magenta]Random Search:[/bold magenta] Strict Joint Pass={r_joint}/{n}")
    console.print(f"SHA-256 Ledger saved: [cyan]{ledger_path}[/cyan]")


if __name__ == "__main__":
    main()

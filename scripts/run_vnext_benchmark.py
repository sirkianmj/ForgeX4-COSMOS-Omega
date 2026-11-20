import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.vnext import AuditLedger, GeneralistFoundry, SandboxClient, load_catalog


def main():
    console = Console()
    console.rule("[bold cyan]COSMOS-Ω vNext: 16-Target Multi-Archetype Kernel Benchmark[/bold cyan]")

    client = SandboxClient()
    client.ensure_running()
    ledger = AuditLedger(PROJECT_ROOT / "artifacts" / "vnext_logs", run_name="core16")
    foundry = GeneralistFoundry(client=client, ledger=ledger, seed=42)

    targets = load_catalog(PROJECT_ROOT / "targets" / "catalog" / "core_16.yaml", PROJECT_ROOT)
    table = Table(title="COSMOS-Ω vs Baselines (16 Real Targets)")
    table.add_column("Target", style="cyan")
    table.add_column("Type")
    table.add_column("Z3", justify="center")
    table.add_column("COSMOS Benign", justify="right")
    table.add_column("COSMOS Block", justify="right")
    table.add_column("2-Float Block", justify="right")
    table.add_column("Random Block", justify="right")
    table.add_column("Priv Surf", justify="right")

    results = []
    for idx, t in enumerate(targets, 1):
        t0 = time.time()
        console.print(f"[{idx:02d}/{len(targets):02d}] Synthesizing [cyan]{t.id}[/cyan] ({t.archetype})...", end=" ")
        res = foundry.synthesize(t, pop_size=10, generations=5)
        dt = time.time() - t0
        co = res["cosmos_omega"]
        q2 = res["baseline_quantile_2float"]
        rs = res["baseline_random_search"]
        console.print(f"done in {dt:.1f}s | benign={co['benign_pass_rate']*100:.0f}% block={co['attack_block_rate']*100:.0f}% vs 2-float={q2['attack_block_rate']*100:.0f}%")
        results.append(res)
        table.add_row(
            t.id,
            t.archetype,
            "PASS" if co["z3_verified"] else "FAIL",
            f"{co['benign_pass_rate']*100:.0f}%",
            f"{co['attack_block_rate']*100:.0f}%",
            f"{q2['attack_block_rate']*100:.0f}%",
            f"{rs['attack_block_rate']*100:.0f}%",
            f"{co['privilege_surface']:.2f}",
        )

    console.print(table)
    ledger_path = ledger.save()
    c_blk = sum(r["cosmos_omega"]["attack_block_rate"] for r in results) / len(results)
    c_ben = sum(r["cosmos_omega"]["benign_pass_rate"] for r in results) / len(results)
    q_blk = sum(r["baseline_quantile_2float"]["attack_block_rate"] for r in results) / len(results)
    console.print(f"\n[bold green]Mean COSMOS-Ω:[/bold green] Benign={c_ben*100:.1f}% | Attack Block={c_blk*100:.1f}%")
    console.print(f"[bold yellow]Mean Old 2-Float Sentinel:[/bold yellow] Attack Block={q_blk*100:.1f}%")
    console.print(f"SHA-256 Ledger saved: [cyan]{ledger_path}[/cyan]")


if __name__ == "__main__":
    main()

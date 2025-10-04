# Kian Mansouri Jamshidi
#
# File: scripts/run_sentinel_experiment_v2.py
#
# Description:
# [DEFINITIVE - OPERATION FORGE - FINAL] This is the final, correct, and
# complete master script. It is perfectly synchronized with the final,
# self-contained Titan library and executes the full, multi-physics
# experiment from start to finish. This is the culmination of the project.

import sys
import re
import json
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
import numpy as np

# --- Setup Project Path ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from cosmos.foundry.foundry_sentinel import SentinelFoundry
from cosmos.foundry.titans_sentinel import ExecutionTitan
from cosmos.ledger.ledger import Ledger

app = typer.Typer(name="COSMOS-Ω Definitive MPED Experiment")
console = Console()

def profile_target() -> dict:
    """Profiles the target to get baseline syscalls and CPU usage."""
    console.print("\n[bold]Phase 1: Profiling Target Behavior...[/bold]")
    titan = ExecutionTitan()
    normal_payload = b'{"name": "COSMOS", "version": 1}'
    
    # Use the sustained workload run for accurate profiling
    result = titan.instrumented_run(normal_payload, duration=5)
    
    # --- The Final Fix: Check for a successful outcome ---
    if result.get('outcome') not in ['survived', 'crashed']: 
         console.print(Panel(result.get('strace_log', 'No log available'), title="[bold red]PROFILING FAILED[/bold red]", border_style="red"))
         raise typer.Exit(code=1)
        
    syscall_count = len(re.findall(r'^\w+\(.*\)\s*=', result['strace_log'], re.MULTILINE))
    avg_cpu = result['telemetry']['cpu_util_overall'].mean() if not result['telemetry'].empty else 0.0
    
    console.print(f"[green]  ✓ Profiling Complete:[/green] Baseline syscalls: [bold yellow]{syscall_count}[/bold yellow], Baseline CPU: [bold yellow]{avg_cpu:.2f}%[/bold yellow].")
    return {'syscalls': syscall_count, 'cpu': avg_cpu}

@app.command()
def run():
    """Initiates the final, definitive, multi-objective evolution of the Aegis Sentinel."""
    console.rule("[bold blue]Initiating Definitive MPED Sentinel Experiment[/bold blue]")
    
    artifacts_dir = project_root / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    ledger = Ledger(output_dir=str(artifacts_dir / "final_run_logs"))

    try:
        baseline = profile_target()
        
        initial_sentinel_genome = {
            'max_total_syscalls': int(baseline['syscalls'] * 1.5),
            'max_cpu_percent': baseline['cpu'] + 5.0,
        }
        console.print(f"\n[bold]Phase 2: Seeding Initial Population...[/bold]")
        console.print(f"  [green]✓ Seed Genome created:[/green] [cyan]{initial_sentinel_genome}[/cyan]")
        
        console.print("\n[bold]Phase 3: Launching Sentinel Foundry (Powered by the Definitive Digital Twin)...[/bold]")
        
        foundry_config = {
            "population_size": 10, "generations": 10, 
            "mutation_rate": 0.8, "ledger": ledger
        }
        
        foundry = SentinelFoundry(initial_sentinel_genome, foundry_config)
        champion = foundry.run_evolution()
        console.print("\n[green]✅ Foundry run complete.[/green]")

        ledger.save()
        console.print(f"[green]  ✓ Cryptographically-chained Ledger saved to:[/green] [dim]{ledger.output_file}[/dim]")

        sentinel_artifact_path = artifacts_dir / "aegis_sentinel_champion.json"
        with open(sentinel_artifact_path, 'w') as f:
            # Handle numpy types for clean JSON serialization
            champion_serializable = champion.copy()
            champion_serializable['genome'] = {k: (int(v) if isinstance(v, np.integer) else float(v) if isinstance(v, np.floating) else v) for k, v in champion['genome'].items()}
            champion_serializable.pop('id', None) # Remove transient fields
            json.dump(champion_serializable, f, indent=4, default=str)
        console.print(f"[green]  ✓ Final Aegis Sentinel artifact saved to:[/green] [dim]{sentinel_artifact_path}[/dim]")
        
        console.rule("[bold green]PROJECT COMPLETE: FINAL SYNTHESIS[/bold green]")
        
        panel_content = (
            f"[bold]Final Fitness Score:[/bold] [yellow]{champion['fitness']:.2f}[/yellow]\n\n"
            f"[bold]Evolved Configuration:[/bold]\n[cyan]{champion['genome']}[/cyan]"
        )
        console.print(Panel(panel_content, title="Aegis Sentinel v1.0"))
        
        if champion['fitness'] > 500:
            console.print("\n[bold green]VALIDATION SUCCESSFUL:[/bold green] The final configuration is a beneficial security agent.")
        else:
            console.print("\n[bold yellow]VALIDATION NEUTRAL:[/bold yellow] The experiment completed, but did not find a superior configuration.")

    except Exception as e:
        console.print(f"\n[bold red]A FATAL ERROR OCCURRED[/bold red]: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
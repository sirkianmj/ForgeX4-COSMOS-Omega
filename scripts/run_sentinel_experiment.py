# Kian Mansouri Jamshidi
#
# File: scripts/run_sentinel_experiment.py
#
# Description:
# [DEFINITIVE - V2 - FORENSIC PROFILING] This is the final, correct script.
# It includes robust error reporting in the profiling stage to provide
# definitive evidence in case of a pre-flight failure.

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
import re

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from cosmos.foundry.foundry_sentinel import SentinelFoundry
from cosmos.foundry.titans_sentinel import ExecutionTitan

app = typer.Typer(name="COSMOS-Ω Sentinel Experiment")
console = Console()

def profile_target() -> dict:
    """
    Profiles the target to find the baseline number of system calls.
    Includes robust error reporting.
    """
    console.print("\n[bold]Phase 1: Profiling Target Behavior...[/bold]")
    titan = ExecutionTitan()
    normal_payload = b'1'  # mode 1 = benign I/O
    
    permissive_genome = {'max_cpu_percent': 500.0}  # M5 P-cores can exceed 100%
    result = titan.instrumented_run(normal_payload, genome=permissive_genome, timeout=5)
    if result['outcome'] != 'survived':
        # --- FORENSIC REPORTING ---
        error_panel = Panel(
            str(result),
            title="[bold red]Compiler/Execution Error[/bold red]",
            border_style="red"
        )
        console.print(error_panel)
        raise RuntimeError(f"Profiling failed! The target could not be compiled or executed normally. Outcome: {result['outcome']}")
        
    snapshot = result.get('telemetry_snapshot', {})
    baseline_cpu = snapshot.get('max_cpu_percent', 0.0)
    console.print(f"[green]  ✓ Profiling Complete:[/green] Peak CPU: [bold yellow]{baseline_cpu:.2f}%[/bold yellow].")
    return {'max_cpu': baseline_cpu}

@app.command()
def run():
    """Initiates a full, multi-objective evolution of an Aegis Sentinel."""
    console.rule("[bold blue]Initiating Aegis Sentinel Experiment[/bold blue]")
    try:
        baseline_syscalls = profile_target()
        
        initial_sentinel_genome = {'max_cpu_percent': max(baseline_syscalls['max_cpu'] * 2.5, 25.0)}
        console.print(f"\n[bold]Phase 2: Seeding Initial Population...[/bold]")
        console.print(f"  [green]✓ Seed Genome created:[/green] [cyan]{initial_sentinel_genome}[/cyan]")
        
        console.print("\n[bold]Phase 3: Launching Sentinel Foundry...[/bold]")
        foundry_config = {
            "population_size": 20, "generations": 40,
            "mutation_rate": 0.5, "elitism_count": 2,
        }
        
        foundry = SentinelFoundry(foundry_config)
        champion = foundry.run_evolution()

        # Save the champion artifact
        import json
        from pathlib import Path as _P
        prod = {}
        if "max_cpu_percent" in champion["genome"]:
            prod["max_cpu_percent"] = round(champion["genome"]["max_cpu_percent"] * 1.10, 4)
        if "max_resident_memory_bytes" in champion["genome"]:
            prod["max_resident_memory_bytes"] = int(champion["genome"]["max_resident_memory_bytes"] * 1.10)
        (_P("artifacts") / "aegis_sentinel_champion.json").write_text(
            json.dumps({"genome": champion["genome"], "fitness": champion["fitness"],
                        "production_genome_10pct_margin": prod}, indent=2)
        )
        console.print("\n[green]✅ Foundry run complete.[/green]")

        console.rule("[bold green]Experiment Complete: Aegis Sentinel Champion[/bold green]")
        panel_content = (
            f"[bold]Final Fitness Score:[/bold] [yellow]{champion['fitness']:.2f}[/yellow]\n\n"
            f"[bold]Hardened Configuration:[/bold]\n[cyan]{champion['genome']}[/cyan]"
        )
        console.print(Panel(panel_content, title="Champion Genome"))
        
        if champion['fitness'] > 0:
            console.print("\n[bold green]SUCCESS:[/bold green] The foundry evolved a beneficial security configuration.")
        else:
            console.print("\n[bold yellow]NEUTRAL RESULT:[/bold yellow] The foundry ran successfully but did not improve upon the baseline.")

    except Exception as e:
        console.print(f"\n[bold red]A FATAL ERROR OCCURRED[/bold red]")
        console.print(e)

if __name__ == "__main__":
    app()
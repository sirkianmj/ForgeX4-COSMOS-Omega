# Kian Mansouri Jamshidi
#
# File: scripts/run_sentinel_benchmark.py
#
# Description:
# [DEFINITIVE - OPERATION SENTINEL] This is a NEW file. It is the top-level
# entry point for the new Sentinel architecture. It initializes and runs the
# SentinelFoundry to evolve a hardened security agent configuration.

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel

# --- Setup Project Path ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import the new, separate Sentinel Foundry
from cosmos.foundry.foundry_sentinel import SentinelFoundry

app = typer.Typer(name="COSMOS-Ω Sentinel Evolution Benchmark")
console = Console()

@app.command()
def run():
    """
    Initiates the full, multi-objective evolution of an Aegis Sentinel configuration.
    """
    console.rule("[bold blue]Initiating Aegis Sentinel Synthesis[/bold blue]")

    # --- Initial State Configuration ---
    # This is the "base genome" for our sentinel. It's a simple configuration.
    initial_sentinel_genome = {
        'max_total_syscalls': 200,
    }
    
    # Configuration for the evolutionary run
    foundry_config = {
        "population_size": 10,
        "generations": 5, # Keep this low for a quick validation run
        "mutation_rate": 0.8,
        "elitism_count": 2,
    }

    try:
        # --- Launch the Foundry ---
        console.print("\n[bold]Launching Sentinel Foundry...[/bold]")
        foundry = SentinelFoundry(initial_sentinel_genome, foundry_config)
        champion = foundry.run_evolution()
        console.print("\n[green]✅ Foundry run complete.[/green]")

        # --- Report the Final Champion ---
        console.rule("[bold green]Synthesis Complete: Aegis Sentinel Champion[/bold green]")
        
        panel_content = (
            f"[bold]Final Fitness Score:[/bold] [yellow]{champion['fitness']:.2f}[/yellow]\n\n"
            f"[bold]Hardened Configuration:[/bold]\n[cyan]{champion['genome']}[/cyan]"
        )
        console.print(Panel(panel_content, title="Champion Genome"))
        
        console.print("\n[bold]This configuration represents the synthesized ruleset for the Aegis Sentinel.[/bold]")
        console.print("It has been evolved to maximize security (detecting attacks) while minimizing performance overhead.")

    except Exception as e:
        console.print(f"\n[bold red]A FATAL ERROR OCCURRED DURING EVOLUTION[/bold red]")
        console.print(e)
        # It's helpful to see the full traceback for debugging
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    app()
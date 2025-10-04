#
# ForgeX4 COSMOS-Ω: Final Experiment Runner
# Project Director: Kian Mansouri Jamshidi
# AI Lead Engineer: 
#
# Description:
# [DEFINITIVE - V5 - FINAL RUNNER]
# This is the final, clean script to run the complete, end-to-end COSMOS-Ω foundry.
# It correctly initializes the final "Hybrid Execution" foundry and Titans
# and includes the "Black Box Recorder" for robust error handling.
# This is the definitive execution script for the project.
#

import sys
import traceback
from pathlib import Path
import json

# Ensure the cosmos module is in the Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.foundry.foundry_sentinel import SentinelFoundry
from cosmos.ledger.ledger import Ledger
from rich.console import Console
from rich.panel import Panel

def main():
    """Main function to configure and run the final experiment."""
    console = Console()
    console.rule("[bold green]COSMOS-Ω: Starting Final Experiment (v5 - Final Runner)[/bold green]")

    # --- Configuration ---
    config = {
        "population_size": 10,
        "generations": 10,
        "mutation_rate": 0.8,
        "elitism_count": 2,
    }

    initial_genome = {
        'max_total_syscalls': 100,
    }

    # --- Setup Artifacts Directory & Ledger ---
    artifacts_dir = PROJECT_ROOT / "artifacts" / "final_run_logs"
    artifacts_dir.mkdir(exist_ok=True)
    ledger = Ledger(artifacts_dir)
    config["ledger"] = ledger

    try:
        # ---
        # THE CORE EXECUTION
        # ---
        console.print("Initializing Sentinel Foundry with Hybrid Execution Titans...")
        foundry = SentinelFoundry(initial_genome=initial_genome, config=config)
        
        console.print("\nStarting evolution...")
        champion = foundry.run_evolution()
        
        # ---
        # SUCCESS PATH
        # ---
        console.rule("[bold green]MISSION COMPLETE[/bold green]", style="green")
        
        champion_path = artifacts_dir / "aegis_sentinel_champion.json"
        with open(champion_path, 'w') as f:
            json.dump(champion, f, indent=4)
        console.print(f"Final Champion artifact saved to: [cyan]{champion_path}[/cyan]")
        
        console.print(f"Complete evolutionary ledger saved automatically in: [cyan]{artifacts_dir}[/cyan]")

    except Exception as e:
        # ---
        # FAILURE PATH (BLACK BOX RECORDER)
        # ---
        title = "[bold red]CATASTROPHIC SYSTEM FAILURE DETECTED[/bold red]"
        error_text = (
            f"[bold]Exception Type:[/bold] {type(e).__name__}\n"
            f"[bold]Error Message:[/bold] {e}\n\n"
            f"[bold]Full Traceback:[/bold]\n{traceback.format_exc()}"
        )
        console.print(Panel(error_text, title=title, border_style="red"))
        
        console.rule("[bold yellow]ATOM DEBUGGER: SAVING CRASH DATA[/bold yellow]", style="yellow")
        if ledger and ledger.events:
            ledger.save()
            console.print(f"Partial ledger has been saved to its default log file in the artifacts directory.")
        else:
            console.print("[yellow]Ledger was empty. Crash likely occurred during initialization.[/yellow]")
            
        console.rule("[bold red]Run Aborted[/bold red]", style="red")

if __name__ == "__main__":
    main()
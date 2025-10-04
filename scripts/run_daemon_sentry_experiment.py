#
# File: scripts/run_daemon_sentry_experiment.py (v6.1 - "OMEGA'S GRACE" - DEFINITIVE)
#
# This is the final, definitive, and correct version of the experiment script.
# It integrates the "Swarm" architecture for speed, the "Architect" foundry
# for intelligence, and restores the powerful, multi-objective "Omega Fitness
# Function" from the original, successful cJSON experiment.
#
import sys
import time
import json
import os
import multiprocessing
import pandas as pd
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any

# --- Project Setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.foundry.foundry_pathfinder import SentinelFoundry
from cosmos.foundry.titans_pathfinder import ExecutionTitan, _engineer_fingerprint_from_telemetry
from cosmos.ledger.ledger import Ledger

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# --- Worker Setup ---
def evaluate_genome_worker(individual: dict, worker_id: int) -> dict:
    titan = ExecutionTitan(worker_id=worker_id)
    genome = individual['genome']
    benign_result = titan.instrumented_run(payload_type="benign", genome=genome)
    malicious_result = titan.instrumented_run(payload_type="malicious", genome=genome)
    return {
        'id': individual['id'], 'genome': genome,
        'benign_outcome': benign_result['outcome'], 'benign_telemetry': benign_result['raw_telemetry'],
        'attack_outcome': malicious_result['outcome'], 'attack_telemetry': malicious_result['raw_telemetry']
    }

class ExperimentOrchestrator:
    """The definitive, final orchestrator for the Architect Swarm experiment."""
    def __init__(self, config: dict):
        self.console = Console()
        self.config = config
        try:
            self.foundry = SentinelFoundry(self.config)
            self.ledger = Ledger(output_dir=str(PROJECT_ROOT / "artifacts/architect_swarm_logs"))
        except Exception as e:
            self.console.print(f"[bold red]FATAL: FAILED TO INITIALIZE.[/bold red]\n{e}")
            sys.exit(1)

    def calculate_omega_fitness(self, truth_packet: dict) -> dict:
        """The restored and adapted Omega Fitness Function."""
        total_fitness, breakdown = 0, {}
        
        # --- 1. Correctness ---
        # The benign run MUST survive. A policy_violation is a critical failure.
        is_correct = (truth_packet['benign_outcome'] == 'survived')
        if is_correct:
            benign_analysis = self.foundry.performance_titan.analyze(truth_packet['benign_telemetry'])
            confidence = benign_analysis.get('confidence', {}).get(str(self.foundry.normal_profile_id), 0.0)
            breakdown['Correctness'] = 500 * (confidence ** 2)
        else:
            breakdown['Correctness'] = -3000.0 # Massive penalty for False Positives
        total_fitness += breakdown['Correctness']
        
        # --- 2. Security ---
        # The malicious run MUST be stopped by a policy violation.
        is_secure = (truth_packet['attack_outcome'] == 'policy_violation')
        if is_secure:
            # Reward for speed of detection
            reaction_time = len(truth_packet['attack_telemetry'])
            breakdown['Security (Speed)'] = 1000 / (1 + reaction_time)
        else:
            breakdown['Security (Speed)'] = -3000.0 # Massive penalty for False Negatives
        total_fitness += breakdown['Security (Speed)']

        # --- 3. Penalties (only apply if the policy is viable) ---
        if is_correct and is_secure:
            # Performance Penalty based on CPU overhead of the benign run
            fingerprint = _engineer_fingerprint_from_telemetry(truth_packet['benign_telemetry'], self.foundry.performance_titan.feature_list)
            cpu_overhead = fingerprint['cpu_percent_total_mean'].iloc[0]
            breakdown['Perf. Penalty'] = - (cpu_overhead ** 1.5)
            total_fitness += breakdown['Perf. Penalty']
            
            # Elegance Penalty for complexity
            complexity = len(json.dumps(truth_packet['genome']))
            breakdown['Elegance Penalty'] = - (complexity / 100.0)
            total_fitness += breakdown['Elegance Penalty']
            
        truth_packet.update({'fitness': total_fitness, 'breakdown': breakdown})
        return truth_packet

    def run(self):
        self.console.rule("[bold blue]COSMOS-Ω: Architect Swarm Experiment (OMEGA)[/bold blue]")
        try:
            self.console.print("[yellow]Calibrating...[/yellow]")
            self.foundry.calibrate()
            self.console.print(f"[green]Calibration Complete.[/green] 'Normal' Profile is [bold cyan]{self.foundry.normal_profile_id}[/bold cyan]")
        except Exception as e:
            self.console.print(f"[bold red]FATAL: Calibration failed![/bold red]\n{e}"); return

        self.console.print("[yellow]Initializing Genesis Population of Architects...[/yellow]")
        self.foundry._initialize_population()
        
        num_workers = max(1, multiprocessing.cpu_count() - 1)
        self.console.print(f"[cyan]Deploying Swarm with {num_workers} parallel workers...[/cyan]")
        
        with Progress(SpinnerColumn(), TextColumn("[...]{task.description}"), BarColumn(), TimeElapsedColumn(), console=self.console) as progress:
            main_task = progress.add_task("[green]Total Evolution", total=self.foundry.generations)
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                for gen in range(self.foundry.generations):
                    self.console.rule(f"Epoch {gen}")
                    gen_task = progress.add_task(f"[cyan]  Evaluating Genomes", total=self.foundry.population_size)
                    
                    futures = { executor.submit(evaluate_genome_worker, ind, i % num_workers): ind for i, ind in enumerate(self.foundry.population) }
                    raw_results = [future.result() for future in as_completed(futures)]
                    
                    # Grade all results using the Omega Fitness Function
                    scored_results = [self.calculate_omega_fitness(res) for res in raw_results]
                    
                    # --- ARCHITECT DEBUGGER ---
                    self.console.print("\n[bold magenta]--- ARCHITECT DEBUGGER & OMEGA FITNESS ANALYSIS ---[/bold magenta]")
                    for res in scored_results:
                        is_correct = res['breakdown']['Correctness'] > 0
                        is_secure = res['breakdown']['Security (Speed)'] > 0
                        self.console.print(f"GID-{res['id']:<2} | Complexity: {len(json.dumps(res['genome']))} chars | Final Fitness: [bold {'green' if res['fitness'] > 0 else 'red'}]{res['fitness']:>+9.2f}[/bold {'green' if res['fitness'] > 0 else 'red'}]")
                        self.console.print(f"  ├─ [blue]Benign Run...[/blue]  Outcome: [bold {'green' if is_correct else 'red'}]{res['benign_outcome']}[/bold {'green' if is_correct else 'red'}] -> Score: {res['breakdown']['Correctness']:.2f}")
                        self.console.print(f"  └─ [red]Malicious Run...[/red] Outcome: [bold {'green' if is_secure else 'red'}]{res['attack_outcome']}[/bold {'green' if is_secure else 'red'}] (Reaction Time: {len(res['attack_telemetry'])} ticks) -> Score: {res['breakdown']['Security (Speed)']:.2f}\n")
                    self.console.print("[bold magenta]--- END DEBUGGER ---[/bold magenta]\n")

                    for result in scored_results:
                        for pop_ind in self.foundry.population:
                            if pop_ind['id'] == result['id']: pop_ind.update(result); break
                    self.foundry._evolve_population()
                    self.ledger.record_event(block_height=gen + 1, event_type="GENERATION_COMPLETE", details={"generation": gen, "champion": self.foundry.population[0].copy()})
                    progress.remove_task(gen_task)
                    progress.update(main_task, advance=1)

        if self.foundry.population:
            final_champion = max(self.foundry.population, key=lambda x: x.get('fitness', -9999))
            self.ledger.save()
            self.console.rule("[bold green]ARCHITECT EXPERIMENT COMPLETE[/bold green]", style="green")
            champion_genome_str = json.dumps(final_champion.get('genome', {}), indent=2)
            self.console.print(Panel(Syntax(champion_genome_str, "json", theme="monokai", line_numbers=True), title="[bold cyan]Final Champion 'Architect' Genome[/bold cyan]", border_style="cyan"))
            decon_table = Table(title="[bold cyan]Champion Fitness Deconstruction[/bold cyan]")
            decon_table.add_column("Component"); decon_table.add_column("Score")
            for k, v in final_champion.get('breakdown', {}).items(): decon_table.add_row(k, f"{v:+.2f}")
            decon_table.add_row("[bold]Final Fitness[/bold]", f"[bold]{final_champion.get('fitness', 0):+.2f}[/bold]")
            self.console.print(decon_table)
            self.console.print(f"\n[bold] Ledger saved to:[/bold] [yellow]{self.ledger.ledger_path}[/yellow]")
        else:
            self.console.print("\n[bold red]Execution failed to produce a final champion.[/bold red]")

def main():
    config = {"population_size": 20, "generations": 25, "elitism_count": 2, "crossover_rate": 0.7, "mutation_rate": 0.9}
    orchestrator = ExperimentOrchestrator(config=config)
    orchestrator.run()

if __name__ == "__main__":
    if 'pandas' not in sys.modules: import pandas as pd
    try: multiprocessing.set_start_method('fork', force=True)
    except (ValueError, RuntimeError): pass
    main()
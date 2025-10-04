#
# File: scripts/run_cosmic_debugger.py
#
# Description:
# [DEFINITIVE - V9.0 "OPERATION AUDIT" - THE FINAL OBSERVATORY]
# This is the final, definitive run script. It fully integrates the
# blockchain-style Ledger to fulfill the project's core XAI requirement.
#
# KEY UPGRADES:
# 1. Full Ledger Integration: The script now meticulously records every key
#    event in the evolutionary process—from genesis to the final champion—
#    into a cryptographically-chained JSON log.
# 2. Forensic Detail: Each generation's complete evaluation results are
#    logged, providing an unassailable audit trail for the AI's decisions.
# 3. Automated Save: The Ledger is automatically saved upon completion,
#    producing the final, tangible XAI artifact of the project.
#

import sys
import time
import threading
import traceback
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.foundry.foundry_sentinel import SentinelFoundry
from cosmos.ledger.ledger import Ledger
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text

# --- Global State & Worker Setup ---
foundry_instance_for_workers = None
def evaluate_genome_worker(individual: dict) -> dict:
    return foundry_instance_for_workers._evaluate_genome(individual)

class CosmicDebugger:
    FREEZE_THRESHOLD_SECONDS = 300

    def __init__(self, foundry: SentinelFoundry):
        global foundry_instance_for_workers
        foundry_instance_for_workers = foundry
        self.foundry = foundry
        self.console = Console()
        # --- LEDGER INITIALIZATION ---
        self.ledger = Ledger(output_dir=str(PROJECT_ROOT / "artifacts/logs"))
        self.layout = self._create_layout()
        self.is_running = True
        self.live_context = None
        self.truth_reports = []
        self.last_heartbeat = time.time()
        self.current_status = "Initializing..."

    def _create_layout(self) -> Layout:
        layout = Layout()
        layout.split(Layout(name="header", size=3), Layout(ratio=1, name="main"), Layout(size=3, name="footer"))
        layout["main"].split_row(Layout(name="side", ratio=1), Layout(name="body", ratio=1))
        return layout

    def _watchdog_thread(self):
        main_thread = threading.main_thread()
        while self.is_running:
            time.sleep(5)
            if time.time() - self.last_heartbeat > self.FREEZE_THRESHOLD_SECONDS:
                if self.live_context: self.live_context.stop()
                self.console.print(Panel(Text.from_markup(f"[bold red]CRITICAL: FREEZE DETECTED!\n\nStatus was: '{self.current_status}'"), title="[bold yellow]Intelligent Freeze Detector[/bold yellow]", border_style="bold red"))
                stack_trace = "".join(traceback.format_stack(sys._current_frames()[main_thread.ident]))
                self.console.print(f"[bold]Main thread stack trace:[/bold]\n[yellow]{stack_trace}[/yellow]")
                os._exit(1)

    def run(self):
        watchdog = threading.Thread(target=self._watchdog_thread, daemon=True)
        watchdog.start()
        try:
            with Live(self.layout, screen=True, redirect_stderr=False, transient=True) as live:
                self.live_context = live
                self.current_status = "Calibrating Digital Twin..."
                self._update_dashboard(live, "Calibrating...")
                self.foundry.calibrate()
                
                self.foundry._initialize_population()
                # --- LEDGER EVENT: RECORD INITIAL POPULATION ---
                self.ledger.record_event(
                    block_height=0,
                    event_type="INITIAL_POPULATION_CREATED",
                    details={"population": [ind.copy() for ind in self.foundry.population]}
                )
                self._update_dashboard(live, "Initialized")

                for gen in range(self.foundry.generations):
                    self.foundry.epoch = gen
                    self.current_status = f"Epoch {gen}: Evaluating Population..."
                    self.last_heartbeat = time.time()
                    self._update_dashboard(live, f"Epoch {gen}: Submitting evaluation tasks...")
                    
                    self.truth_reports.clear()
                    results = []
                    max_workers = max(1, os.cpu_count() // 2)
                    with ProcessPoolExecutor(max_workers=max_workers) as executor:
                        futures = {executor.submit(evaluate_genome_worker, ind): ind for ind in self.foundry.population}
                        for future in as_completed(futures):
                            results.append(future.result())
                    
                    self.truth_reports = results
                    # --- LEDGER EVENT: RECORD FULL EVALUATION RESULTS ---
                    self.ledger.record_event(
                        block_height=gen + 1,
                        event_type="EVALUATION_COMPLETE",
                        details={"generation": gen, "evaluation_results": results}
                    )
                    
                    for result in results:
                        for pop_ind in self.foundry.population:
                            if pop_ind['id'] == result['id']: pop_ind.update(result); break
                    
                    self._update_dashboard(live, f"Epoch {gen}: Evaluation Complete")
                    self.foundry._selection()
                    
                    # --- LEDGER EVENT: RECORD THE GENERATION'S CHAMPION ---
                    self.ledger.record_event(
                        block_height=gen + 1,
                        event_type="CHAMPION_UPDATED",
                        details={"generation": gen, "champion": self.foundry.population[0].copy()}
                    )

                    self._update_dashboard(live, f"Epoch {gen}: Selection Complete")
                    self.foundry._mutate_population()
                    self._update_dashboard(live, f"Epoch {gen}: Evolving...")

                champion = max(self.foundry.population, key=lambda x: x['fitness'])
                # --- LEDGER EVENT: RECORD THE FINAL CHAMPION ---
                self.ledger.record_event(
                    block_height=self.foundry.generations + 1,
                    event_type="FINAL_CHAMPION_SYNTHESIZED",
                    details={"final_champion": champion.copy()}
                )

        finally:
            self.is_running = False
            # --- LEDGER ACTION: SAVE THE COMPLETE LOG ---
            self.ledger.save()

        self.console.clear()
        self.console.rule("[bold green]SENTINEL SYNTHESIS COMPLETE[/bold green]", style="green")
        
        champion_table = Table(title="[bold cyan]FINAL CHAMPION POLICY[/bold cyan]")
        champion_table.add_column("Parameter"); champion_table.add_column("Value")
        for k, v in champion.get('genome', {}).items(): champion_table.add_row(k, f"{v:.2f}")
        
        decon_table = Table(title="[bold cyan]Champion Fitness Deconstruction[/bold cyan]")
        decon_table.add_column("Component"); decon_table.add_column("Score")
        total = sum(champion.get('breakdown', {}).values())
        for k, v in champion.get('breakdown', {}).items(): decon_table.add_row(k, f"{v:+.2f}")
        decon_table.add_row("[bold]Final Fitness[/bold]", f"[bold]{total:+.2f}[/bold]")
        
        self.console.print(champion_table)
        self.console.print(decon_table)
        if total > 0:
            self.console.print("\n[bold green]SUCCESS: A positive-scoring, effective security policy was synthesized.[/bold green]")
        else:
             self.console.print("\n[bold yellow]OUTCOME: The system ran, but did not discover a positive-scoring champion policy.[/bold yellow]")


    def _update_dashboard(self, live: Live, footer_status: str):
        self.foundry.population.sort(key=lambda x: x['fitness'], reverse=True)
        pop_table = Table(title=f"Population Status (Epoch {self.foundry.epoch})", padding=(0, 1))
        pop_table.add_column("Rank"); pop_table.add_column("GID"); pop_table.add_column("Fitness"); pop_table.add_column("Genome")
        for i, ind in enumerate(self.foundry.population):
             genome_str = ", ".join([f"{k.replace('_',' ')}: {v:.1f}" for k, v in ind.get('genome', {}).items()])
             pop_table.add_row(str(i+1), str(ind['id']), f"{ind['fitness']:+.2f}", genome_str)

        truth_panels = []
        for report in sorted(self.truth_reports, key=lambda x: x['fitness'], reverse=True):
            color = "green" if report.get('fitness', 0) > 0 else "red"
            genome_str = ", ".join([f"{k.replace('_',' ')}: {v:.1f}" for k, v in report.get('genome', {}).items()])
            outcome_panel = Panel(
                f"[bold]Breakdown:[/bold] {' | '.join([f'{k}: {v:+.1f}' for k, v in report.get('breakdown',{}).items()])}",
                title=f"GID {report['id']} | Genome: {genome_str} | Fitness: {report.get('fitness', 0):+.2f}",
                border_style=color,
                padding=(1,2)
            )
            truth_panels.append(outcome_panel)

        self.layout["header"].update(Panel(Text("COSMOS-Ω: Cosmic Debugger v9.0 (Audit)", justify="center"), style="bold blue"))
        self.layout["side"].update(Panel(pop_table, title="[bold]Population[/bold]"))
        self.layout["body"].update(Panel(Layout("\n".join(str(p) for p in truth_panels)), title="[bold]The Truth Panel[/bold]"))
        self.layout["footer"].update(Panel(Text(f"Status: {footer_status} | Normal Profile ID: {self.foundry.normal_profile_id}", justify="left"), style="green"))
        live.refresh()

def main():
    console = Console()
    console.rule("[bold blue]COSMOS-Ω: Launching Operation Audit[/bold blue]")
    
    config = {"population_size": 10, "generations": 10}
    
    try:
        foundry = SentinelFoundry(config=config)
    except Exception:
        console.print(Panel(Text.from_markup("[bold red]FATAL: FAILED TO INITIALIZE FOUNDRY\n\n" + traceback.format_exc()), title="[bold red]Initialization Failure[/bold]"))
        sys.exit(1)
    
    debugger = CosmicDebugger(foundry=foundry)
    debugger.run()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
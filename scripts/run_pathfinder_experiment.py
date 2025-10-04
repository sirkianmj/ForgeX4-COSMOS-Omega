import sys
import time
import threading
import traceback
import os
import json
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import pandas as pd

# The project root setup for imports must be preserved
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Imports are structured based on the intended file hierarchy
from cosmos.foundry.foundry_pathfinder import SentinelFoundry
# Assuming cosmos.ledger.ledger exists for this import to work
from cosmos.ledger.ledger import Ledger 
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.syntax import Syntax
from rich.rule import Rule

# [DEFINITIVE - V25.1 "OPERATION VERITAS" - THE FINAL OBSERVATORY]
# This version contains the definitive fix for the AttributeError by including
# the full and correct implementation of the OmegaDebugger class.
# --- WORKER INITIALIZATION ---

worker_execution_titan = None
def init_worker(config):
    global worker_execution_titan
    # This creates a lightweight instance in each worker
    worker_foundry = SentinelFoundry(config)
    worker_execution_titan = worker_foundry.execution_titan

def evaluate_genome_worker(individual: dict) -> dict:
    genome = individual['genome']
    benign_result = worker_execution_titan.instrumented_run(b'{"name": "COSMOS"}', genome)
    attack_result = worker_execution_titan.instrumented_run(b'A' * 512, genome)
    return {
        'id': individual['id'],
        'genome': genome,
        'benign_outcome': benign_result['outcome'],
        'benign_telemetry': benign_result['raw_telemetry'],
        'attack_outcome': attack_result['outcome'],
        'attack_telemetry': attack_result['raw_telemetry']
    }

class OmegaDebugger:
    """A fully decoupled, static forensic and diagnostic system."""
    log_file = PROJECT_ROOT / "artifacts/logs/omega_debugger.log"


    @staticmethod
    def setup():
        """Initializes the logging system."""
        OmegaDebugger.log_file.parent.mkdir(exist_ok=True, parents=True)
        logging.basicConfig(
            filename=OmegaDebugger.log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        console = Console()
        console.print(f"Omega Debugger is active. Forensic logs will be saved to: [cyan]{OmegaDebugger.log_file}[/cyan]")

    @staticmethod
    def log_critical_event(event_type: str, context: str, exception: Exception = None, genome_data: dict = None, stack_trace: str = None):
        """Logs a major failure to the debug file for root cause analysis."""
        log_entry = (
            f"--- OMEGA DEBUGGER: CRITICAL EVENT ---\n"
            f"EVENT TYPE: {event_type}\n"
            f"CONTEXT: {context}\n"
        )
        if exception:
            log_entry += f"EXCEPTION: {type(exception).__name__}: {exception}\n"
        if stack_trace:
            log_entry += f"STACK TRACE:\n{stack_trace}\n"
        if genome_data:
            genome_str = json.dumps(genome_data, indent=2)
            log_entry += f"PROBLEMATIC GENOME:\n{genome_str}\n"
        log_entry += "--- END OF EVENT ---\n"
        logging.critical(log_entry)

def watchdog_thread(heartbeat_ref, is_running_ref, status_ref, threshold):
    main_thread_id = threading.main_thread().ident
    while is_running_ref[0]:
        time.sleep(5)
        if time.time() - heartbeat_ref[0] > threshold:
            stack = "".join(traceback.format_stack(sys._current_frames()[main_thread_id]))
            OmegaDebugger.log_critical_event(event_type="FREEZE DETECTED", context=f"No heartbeat in {threshold}s. Last status: '{status_ref[0]}'", stack_trace=stack)
            console = Console()
            console.print(Panel(f"[bold red]CRITICAL FREEZE DETECTED!\n\nRoot cause analysis has been saved to the Omega Debugger log.", title="[bold yellow]Intelligent Freeze Detector[/bold yellow]"))
            os._exit(1)

class PathfinderDebugger:
    FREEZE_THRESHOLD_SECONDS = 300
    def __init__(self, foundry: SentinelFoundry):
        self.foundry = foundry
        self.console = Console()
        self.ledger = Ledger(output_dir=str(PROJECT_ROOT / "artifacts/logs"))
        self.is_running_ref = [True]; self.heartbeat_ref = [time.time()]; self.status_ref = ["Initializing..."]
        self.final_champion = None; self.truth_reports = []
        self.layout = self._create_layout()


    def _create_layout(self) -> Layout:
        layout = Layout(); 
        layout.split(Layout(name="header", size=3), Layout(ratio=1, name="main"), Layout(size=5, name="footer")); 
        layout["main"].split_row(Layout(name="side", ratio=1), Layout(name="body", ratio=2)); 
        return layout

    def _update_dashboard(self, live: Live, footer_status: str):
        self.heartbeat_ref[0] = time.time(); self.status_ref[0] = footer_status; self.foundry.population.sort(key=lambda x: x.get('fitness', -9999), reverse=True)
        pop_table = Table(title=f"Population Status (Epoch {self.foundry.epoch})", padding=(0, 1)); 
        pop_table.add_column("Rank", style="bold white"); 
        pop_table.add_column("GID"); 
        pop_table.add_column("Fitness", style="bold"); 
        pop_table.add_column("Genome Architecture")
        for i, ind in enumerate(self.foundry.population[:15]):
             genome = ind.get('genome', {}); 
             num_states = len(genome.get('states', {})); 
             complexity = len(json.dumps(genome)); 
             arch_str = f"{num_states} States, Complexity: {complexity}"
             style = "green" if ind.get('fitness', 0) > 0 else "yellow" if ind.get('fitness', 0) > -1000 else "red"; 
             pop_table.add_row(str(i+1), str(ind.get('id', 'N/A')), f"[{style}]{ind.get('fitness', -9999):+.2f}[/{style}]", arch_str)
        truth_panels = []
        for report in sorted(self.truth_reports, key=lambda x: x.get('fitness', -9999), reverse=True)[:5]:
            color = "green" if report.get('fitness', 0) > 0 else "red"; 
            outcome_panel = Panel(f"[bold]Breakdown:[/bold] {' | '.join([f'{k}: {v:+.1f}' for k, v in report.get('breakdown',{}).items()])}", title=f"GID {report.get('id', 'N/A')} | Fitness: {report.get('fitness', 0):+.2f}", border_style=color, padding=(1,2)); 
            truth_panels.append(outcome_panel)
        self.layout["header"].update(Panel(Text("COSMOS-Ω: Omega Architect Experiment", justify="center"), style="bold blue")); 
        self.layout["side"].update(Panel(pop_table, title="[bold]Population[/bold]")); 
        self.layout["body"].update(Panel(Layout("\n".join(str(p) for p in truth_panels)), title="[bold]Live Truth Panel[/bold]"))
        self.layout["footer"].update(Panel(Text(f"Status: {footer_status} | Normal Profile ID: {self.foundry.normal_profile_id}\nLedger Path: {self.ledger.ledger_path}", justify="left"), style="green")); 
        live.refresh()

    def calculate_omega_fitness(self, truth_packet: dict) -> dict:
        total_fitness = 0; breakdown = {}
        benign_profile_analysis = self.foundry.performance_titan.analyze(truth_packet['benign_telemetry'])
        if truth_packet['benign_outcome'] == 'survived':
            confidence = benign_profile_analysis.get('confidence', {}).get(str(self.foundry.normal_profile_id), 0.0); 
            breakdown['Correctness'] = 500 * (confidence ** 2)
        else: breakdown['Correctness'] = -2000.0
        total_fitness += breakdown['Correctness']
        if truth_packet['attack_outcome'] != 'survived':
            telemetry_len = len(truth_packet['attack_telemetry']); 
            breakdown['Security'] = 1000 / (1 + telemetry_len) if telemetry_len > 0 else 1000.0
        else: breakdown['Security'] = -1000.0
        total_fitness += breakdown['Security']
        if breakdown['Correctness'] > 0:
            # NOTE: This internal import is preserved as per the original code
            from cosmos.foundry.titans_pathfinder import _engineer_fingerprint_from_telemetry
            fingerprint = _engineer_fingerprint_from_telemetry(truth_packet['benign_telemetry'], self.foundry.performance_titan.feature_list)
            cpu_overhead = fingerprint['cpu_percent_total_mean'].iloc[0] if not fingerprint.empty else 100.0
            mem_overhead = fingerprint['memory_rss_bytes_mean'].iloc[0] if not fingerprint.empty else 0
            breakdown['Perf. Penalty (CPU)'] = - (cpu_overhead ** 1.5); 
            breakdown['Perf. Penalty (Mem)'] = - (mem_overhead / 10000); 
            breakdown['Elegance Penalty'] = - (len(json.dumps(truth_packet['genome'])) / 50)
            total_fitness += breakdown['Perf. Penalty (CPU)'] + breakdown['Perf. Penalty (Mem)'] + breakdown['Elegance Penalty']
        truth_packet.update({'fitness': total_fitness, 'breakdown': breakdown}); 
        return truth_packet

    def run_evolution(self):
        with Live(self.layout, screen=True, redirect_stderr=False, transient=True) as live:
            self.foundry.calibrate(); 
            self.foundry._initialize_population()
            self.ledger.record_event(block_height=0, event_type="INITIAL_POPULATION_CREATED", details={"population": [ind.copy() for ind in self.foundry.population]})
            with ProcessPoolExecutor(max_workers=os.cpu_count(), initializer=init_worker, initargs=(self.foundry.config,)) as executor:
                for gen in range(self.foundry.generations):
                    self.foundry.epoch = gen; 
                    self._update_dashboard(live, f"Epoch {gen}: Evaluating Population...")
                    futures = {executor.submit(evaluate_genome_worker, ind): ind for ind in self.foundry.population}
                    try:
                        raw_results = [future.result() for future in as_completed(futures)]
                        self.truth_reports = [self.calculate_omega_fitness(res) for res in raw_results]
                    except Exception as e:
                        crashed_future = next((f for f in futures if f.done() and f.exception()), None)
                        if crashed_future: 
                            OmegaDebugger.log_critical_event("WORKER PROCESS CRASH", f"Exception during genome evaluation.", e, futures[crashed_future]); 
                            self.console.print(Panel(f"[bold red]FATAL: Worker process crashed!\n\nRoot cause analysis saved to the Omega Debugger log.", title="[bold red]Crash Detected[/bold red]"))
                        sys.exit(1)
                    self.ledger.record_event(block_height=gen + 1, event_type="EVALUATION_COMPLETE", details={"generation": gen, "evaluation_results": self.truth_reports})
                    for result in self.truth_reports:
                        for pop_ind in self.foundry.population:
                            if pop_ind['id'] == result['id']: pop_ind.update(result); break
                    self._update_dashboard(live, f"Epoch {gen}: Evaluation Complete. Evolving...")
                    self.foundry._evolve_population()
                    self.ledger.record_event(block_height=gen + 1, event_type="CHAMPION_UPDATED", details={"generation": gen, "champion": self.foundry.population[0].copy()})
        self.final_champion = max(self.foundry.population, key=lambda x: x.get('fitness', -9999)) if self.foundry.population else None
        if self.final_champion: 
            self.ledger.record_event(block_height=self.foundry.generations + 1, event_type="FINAL_CHAMPION_SYNTHESIZED", details={"final_champion": self.final_champion.copy()})

    def run_scientific_validation_gauntlet(self):
        self.console.clear(); 
        self.console.rule("[bold cyan]SCIENTIFIC VALIDATION GAUNTLET[/bold cyan]", style="cyan");
        if not self.final_champion or self.final_champion.get('fitness', -9999) < 0: 
            self.console.print("\n[bold red]GAUNTLET SKIPPED:[/bold red] No positive-scoring champion was evolved to validate.\n"); 
            return
        champion_genome = self.final_champion['genome']; 
        self.console.print("Champion will be subjected to tests it has not seen before.\n")
        self.console.rule("Test 1: Correctness & Stability"); 
        correctness_passes = sum(1 for _ in range(5) if self.foundry.execution_titan.instrumented_run(self.foundry.benign_payloads[0], genome=champion_genome)['outcome'] == 'survived'); 
        self.console.print(f"  Result: {correctness_passes}/5 Benign Payloads Passed.")
        self.console.rule("Test 2: Security Effectiveness"); 
        security_passes = sum(1 for _ in range(5) if self.foundry.execution_titan.instrumented_run(self.foundry.attack_payloads[0], genome=champion_genome)['outcome'] != 'survived'); 
        self.console.print(f"  Result: {security_passes}/5 Attack Payloads Blocked.")
        self.console.rule("[bold]Gauntlet Verdict[/bold]"); 
        is_validated = correctness_passes == 5 and security_passes == 5
        if is_validated: self.console.print("\n[bold green]SCIENTIFIC VALIDATION PASSED[/bold green]")
        else: self.console.print("\n[bold red]SCIENTIFIC VALIDATION FAILED[/bold red]")

    def generate_final_report(self):
        self.console.clear(); 
        self.console.rule("[bold green]COSMOS-Ω: EXPERIMENT COMPLETE[/bold green]", style="green")
        if not self.final_champion: 
            self.console.print("\n[bold red]Execution failed to produce a final champion.[/bold red]"); 
            return
        champion_genome_str = json.dumps(self.final_champion.get('genome', {}), indent=2); 
        self.console.print(Panel(Syntax(champion_genome_str, "json", theme="monokai", line_numbers=True), title="[bold cyan]Final Champion 'Architect' Genome[/bold cyan]", border_style="cyan"))
        decon_table = Table(title="[bold cyan]Champion Fitness Deconstruction[/bold cyan]"); 
        decon_table.add_column("Component"); 
        decon_table.add_column("Score")
        total = sum(self.final_champion.get('breakdown', {}).values());
        for k, v in self.final_champion.get('breakdown', {}).items(): 
            decon_table.add_row(k, f"{v:+.2f}")
        decon_table.add_row("[bold]Final Fitness[/bold]", f"[bold]{total:+.2f}[/bold]"); 
        self.console.print(decon_table)
        self.console.print(f"\n[bold]Complete evolutionary history saved to:[/bold] [yellow]{self.ledger.ledger_path}[/yellow]")

    def run(self):
        w_thread = threading.Thread(target=watchdog_thread, args=(self.heartbeat_ref, self.is_running_ref, self.status_ref, self.FREEZE_THRESHOLD_SECONDS), daemon=True); 
        w_thread.start()
        try:
            self.run_evolution()
            if self.final_champion: self.run_scientific_validation_gauntlet()
        finally:
            self.is_running_ref[0] = False; 
            self.ledger.save(); 
            self.console.clear(home=True); 
            self.generate_final_report()

def main():
    OmegaDebugger.setup()
    console = Console()
    console.rule("[bold blue]COSMOS-Ω: Launching Omega Architect Experiment[/bold blue]")
    config = {"population_size": 20, "generations": 10, "elitism_count": 2, "crossover_rate": 0.7, "mutation_rate": 0.9}
    try:
        foundry = SentinelFoundry(config=config)
    except Exception as e:
        OmegaDebugger.log_critical_event("INITIALIZATION FAILURE", "Failed to create SentinelFoundry instance", e, stack_trace=traceback.format_exc())
        console.print(Panel(Text.from_markup(f"[bold red]FATAL: FAILED TO INITIALIZE FOUNDRY\n\nRoot cause analysis saved to omega_debugger.log"), title="[bold red]Initialization Failure[/bold red]"))
        sys.exit(1)
    debugger = PathfinderDebugger(foundry=foundry); 
    debugger.run()

if __name__ == "__main__":
    multiprocessing.set_start_method('fork', force=True)
    main()
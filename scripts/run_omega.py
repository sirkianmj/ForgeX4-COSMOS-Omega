import sys, time, multiprocessing, os
from pathlib import Path
import psutil, pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cosmos.foundry.foundry_insitu import InSituSentinelFoundry
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# --- OMEGA POINT: The final, correct architecture ---
foundry_instance = None # Global for the workers

def get_telemetry_for_payload(payload: bytes) -> dict:
    """A top-level function for clean telemetry gathering."""
    live_readings = []
    try:
        # Create a worker process to run the payload
        ctx = multiprocessing.get_context('spawn')
        # Use a dummy genome for this telemetry run
        worker = ctx.Process(target=foundry_instance.execution_titan.instrumented_run, args=(payload, {'harden_source': False}))
        worker.start()
        p = psutil.Process(worker.pid)
        p.cpu_percent(interval=None) # Prime the sensor
        time.sleep(0.01)
        with p.oneshot():
            while p.is_running() and worker.is_alive():
                try:
                    live_readings.append({'cpu_percent': p.cpu_percent(interval=None), 'memory_rss': p.memory_info().rss})
                except psutil.NoSuchProcess: break
                time.sleep(0.02)
        worker.join(timeout=15)
        if not live_readings: return {}
        df = pd.DataFrame(live_readings)
        return {'max_cpu_percent': df['cpu_percent'].max(), 'avg_cpu_percent': df['cpu_percent'].mean(), 'max_resident_memory_bytes': df['memory_rss'].max(), 'avg_resident_memory_bytes': df['memory_rss'].mean(), 'observation_duration_ms': len(df) * 20}
    except Exception: return {}

def main():
    console = Console()
    console.rule("[bold green]COSMOS-Ω: OMEGA POINT[/bold green]")
    
    global foundry_instance
    foundry_instance = InSituSentinelFoundry(initial_genome={'harden_source': False}, config={"population_size": 10, "generations": 5, "mutation_rate": 0.5, "elitism_count": 2})
    
    foundry_instance._initialize_population()

    for gen in range(foundry_instance.generations):
        console.rule(f"Epoch {gen}")
        
        # --- THE FINAL, CORRECT EVALUATION LOOP ---
        # 1. Get the true fingerprint of a normal run for this generation
        normal_telemetry = get_telemetry_for_payload(b'{"name":"COSMOS"}')

        # 2. Evaluate each individual against that known truth
        for i in range(len(foundry_instance.population)):
            individual = foundry_instance.population[i]
            # Call the evaluation function WITH the required telemetry
            result = foundry_instance._evaluate_genome(individual, normal_telemetry)
            foundry_instance.population[i].update(result)
            
            fitness = result.get('fitness', 0)
            if fitness > 0: console.print(f"  [green]SUCCESS[/green] - GID {individual['id']} (Harden:{individual['genome']['harden_source']}) -> Fitness: {fitness:.2f}")
            else: console.print(f"  [red]FAILURE[/red] - GID {individual['id']} (Harden:{individual['genome']['harden_source']}) -> Fitness: {fitness:.2f}")

        foundry_instance._selection()
        foundry_instance._mutate_population()

    champion = max(foundry_instance.population, key=lambda x: x['fitness'])
    console.clear(); console.rule("[bold green]OMEGA POINT REACHED[/bold green]", style="green")
    
    champ_table = Table(title="[bold cyan]FINAL CHAMPION GENOME[/bold cyan]")
    champ_table.add_column("Parameter"); champ_table.add_column("Value")
    for k, v in champion.get('genome', {}).items(): champ_table.add_row(k, str(v))
    
    decon_table = Table(title="[bold cyan]Champion Fitness Deconstruction[/bold cyan]")
    decon_table.add_column("Component"); decon_table.add_column("Score")
    total = sum(champion.get('breakdown', {}).values())
    for k, v in champion.get('breakdown', {}).items(): decon_table.add_row(k, f"{v:+.2f}")
    decon_table.add_row("[bold]Final Fitness[/bold]", f"[bold]{total:.2f}[/bold]")
    console.print(champ_table); console.print(decon_table)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
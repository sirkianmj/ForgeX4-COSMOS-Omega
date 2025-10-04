# Kian Mansouri Jamshidi
#
# File: scripts/validate_baseline_engine.py
#
# Description:
# [DEFINITIVE - KEYSTONE V3 - CORRECTED VALIDATION]
# This is the final, correct, unified script. It fixes the flawed validation
# logic. The new, correct definition of success is that the champion
# must SURVIVE ALL tests, both normal and malicious.

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import tempfile
import subprocess
import shutil

# --- Setup ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from cosmos.parser.parser import CParser
from cosmos.foundry.foundry import Foundry

app = typer.Typer(name="COSMOS-Ω Baseline Engine Validator")
console = Console()

# --- Configuration ---
TARGET_CRONOS_FILE = project_root / "data/genomes/cronos/cronos_v0.2.c"
DEFINITIVE_HARNESS = project_root / "data/genomes/uranus/uranus_v1.0.c"

def validate_artifact(champion_path: Path) -> bool:
    """Compiles and runs a validation suite against the final artifact."""
    console.rule("[bold yellow]Stage 2: Validation[/bold yellow]")
    with tempfile.TemporaryDirectory() as temp_dir:
        executable_path = Path(temp_dir) / "champion.out"
        
        console.print(f"  [1] Compiling champion with definitive harness: [cyan]{DEFINITIVE_HARNESS.name}[/cyan]")
        compile_command = ["gcc", "-fno-stack-protector", "-o", str(executable_path), str(champion_path), str(DEFINITIVE_HARNESS)]
        
        compile_result = subprocess.run(compile_command, capture_output=True, text=True)
        if compile_result.returncode != 0:
            console.print("[bold red]  ❌ FATAL: Compilation Failed[/bold red]"); console.print(Panel(compile_result.stderr, title="Compiler Error", border_style="red")); return False
        console.print("[green]  ✅ Champion compiled successfully.[/green]")

        payloads = [b'A' * 256, b'This is a normal input string.']
        results = []
        console.print("\n  [2] Executing resilience tests...")
        for payload in payloads:
            proc = subprocess.run([str(executable_path)], input=payload, capture_output=True, timeout=5)
            results.append({'payload': payload.decode(errors='ignore'), 'outcome': 'survived' if proc.returncode == 0 else 'crashed'})
        
        table = Table(title="Resilience Analysis")
        table.add_column("Payload", style="cyan"); table.add_column("Outcome", style="white")
        for res in results: table.add_row(res['payload'][:30] + "...", res['outcome'])
        console.print(table)
        
        # --- THE DEFINITIVE FIX: The Correct Definition of Success ---
        # A truly hardened champion must survive ALL inputs.
        all_tests_survived = all(r['outcome'] == 'survived' for r in results)
        return all_tests_survived

@app.command()
def run():
    """Performs a full, end-to-end evolution and validation of the baseline engine."""
    console.rule("[bold blue]Initiating Baseline Engine Validation (Keystone V3)[/bold blue]")
    
    console.rule("[bold yellow]Stage 1: Evolution[/bold yellow]")
    parser = CParser()
    champion_artifact_path = project_root / "artifacts/keystone_champion.c"
    
    config = {
        "population_size": 10, "generations": 5, "mutation_rate": 0.8, "elitism_count": 2,
        "tournament_size": 3, "attack_payload": {'payload_len': 128, 'char': 'A', 'terminator': ''}
    }
    
    try:
        initial_ast = parser.parse_file(str(TARGET_CRONOS_FILE))
        foundry = Foundry(initial_cronos_ast=initial_ast, config=config)
        champion = foundry.run_evolution()
        
        if champion and champion.get('genome'):
            champion_code = parser.unparse(champion['genome'])
            with open(champion_artifact_path, "w") as f: f.write("#include <stdio.h>\n#include <string.h>\n\n" + champion_code)
            console.print(f"[green]  ✅ Evolution complete. Champion artifact saved to: [cyan]{champion_artifact_path}[/cyan]")
        else: raise RuntimeError("Foundry failed to produce a champion.")
    except Exception as e:
        console.print(f"\n[bold red]FATAL ERROR DURING EVOLUTION[/bold red]"); console.print(e); return

    console.print("\n\n") # Add spacing before validation
    is_valid = validate_artifact(champion_artifact_path)
    
    if is_valid:
        console.rule("[bold green]VALIDATION SUCCESSFUL[/bold green]")
        console.print("The core engine successfully evolved and validated a hardened artifact.")
    else:
        console.rule("[bold red]VALIDATION FAILED[/bold red]")
        console.print("The evolved artifact did not pass the resilience tests.")

if __name__ == "__main__":
    app()
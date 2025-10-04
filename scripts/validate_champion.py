# Kian Mansouri Jamshidi
#
# File: scripts/validate_champion.py
#
# Description:
# [DEFINITIVE - V2 - EXECUTION FIX] This version adds the critical
# 'if __name__ == "__main__":' block to ensure the script actually runs.

import subprocess
import os
import tempfile
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# --- Configuration ---
project_root = Path(__file__).resolve().parent.parent
# This must point to the correct harness for the champion being tested.
# For cronos_champion.c, the gaia harness is used.
HARNESS_PATH = project_root / "data/genomes/uranus/uranus_v0.1.c" 
# NOTE: The header directory is not needed for this simple, single-file target.

app = typer.Typer(name="COSMOS-Ω Champion Validator")
console = Console()

def run_single_test(executable_path: str, payload: bytes) -> dict:
    """Runs the compiled champion with a single payload and returns the outcome."""
    try:
        proc = subprocess.run(
            [executable_path],
            input=payload,
            capture_output=True,
            timeout=5
        )
        outcome = 'survived' if proc.returncode == 0 else 'crashed'
        return {'payload': payload.decode(errors='ignore'), 'outcome': outcome, 'returncode': proc.returncode}
    except subprocess.TimeoutExpired:
        return {'payload': payload.decode(errors='ignore'), 'outcome': 'timeout', 'returncode': -1}
    except Exception as e:
        return {'payload': payload.decode(errors='ignore'), 'outcome': 'error', 'returncode': -1, 'stderr': str(e)}

@app.command()
def validate(
    champion_path: Path = typer.Argument(..., exists=True, readable=True, help="Path to the hardened champion C file to be validated.")
):
    """
    Compiles and runs a hardened champion against a suite of attack payloads.
    """
    console.rule(f"[bold blue]Initiating Validation for Champion: {champion_path.name}[/bold blue]")

    with tempfile.TemporaryDirectory() as temp_dir:
        executable_path = os.path.join(temp_dir, "champion.out")

        console.print(f"  [1] Compiling champion...")
        # Simplified compile command for single-file champions
        compile_command = [
            "gcc", "-fno-stack-protector",
            "-o", executable_path,
            str(champion_path),
            str(HARNESS_PATH),
        ]
        
        compile_result = subprocess.run(compile_command, capture_output=True, text=True)
        if compile_result.returncode != 0:
            console.print("[bold red]  ❌ FATAL: Compilation Failed[/bold red]")
            console.print(Panel(compile_result.stderr, title="Compiler Error", border_style="red"))
            return

        console.print("[green]  ✅ Champion compiled successfully.[/green]")

        # --- Test Battery ---
        payloads = [
            b'A' * 64,
            b'B' * 256,
            b'C' * 1024,
            b'%s%s%s%s',
            b'This is a normal input string.',
        ]

        console.print("\n  [2] Executing test battery...")
        results = []
        for payload in payloads:
            results.append(run_single_test(executable_path, payload))
        
        console.print("[green]  ✅ Test battery complete.[/green]")

        console.rule("[bold green]Validation Report[/bold green]")
        table = Table(title=f"Resilience Analysis for {champion_path.name}")
        table.add_column("Payload", style="cyan")
        table.add_column("Outcome", style="white")
        table.add_column("Return Code", style="magenta")

        successes = 0
        for res in results:
            style = "red" # Default to fail
            is_attack = "normal" not in res['payload']
            
            if res['outcome'] == 'survived' and not is_attack:
                style = "green"
                successes += 1
            elif res['outcome'] == 'crashed' and is_attack:
                style = "yellow"
                successes += 1
            
            table.add_row(res['payload'][:30] + "...", f"[{style}]{res['outcome']}[/{style}]", str(res['returncode']))

        console.print(table)
        
        final_score = (successes / len(payloads)) * 100
        console.print(f"\n[bold]Final Resilience Score: [yellow]{final_score:.1f}%[/yellow][/bold] ({successes}/{len(payloads)} tests passed)")

# --- THE CRUCIAL EXECUTION BLOCK ---
# This was missing from the previous version. It tells Python to actually
# run the command-line application.
if __name__ == "__main__":
    app()
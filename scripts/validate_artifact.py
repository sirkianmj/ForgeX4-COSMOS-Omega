# Kian Mansouri Jamshidi
#
# File: scripts/validate_artifact.py
#
# Description:
# [DEFINITIVE - BLACK BOX VALIDATION] This is a non-invasive validator.
# It accepts a C file as input and runs a resilience test against it using
# the correct, compatible test harness. It is completely independent of the
# evolutionary engine.

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import tempfile
import subprocess

# --- Setup ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

app = typer.Typer(name="COSMOS-Ω Artifact Validator")
console = Console()

# --- THE CORRECT, COMPATIBLE HARNESS ---
# This harness is designed to work with the output of the baseline synthesis script.
DEFINITIVE_HARNESS = project_root / "data/genomes/uranus/uranus_v1.0.c"

@app.command()
def validate(
    artifact_path: Path = typer.Argument(..., exists=True, readable=True, help="Path to the synthesized C artifact to be validated.")
):
    """
    Compiles and validates a hardened C artifact against a resilience test suite.
    """
    console.rule(f"[bold blue]Initiating Black Box Validation for: {artifact_path.name}[/bold blue]")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        executable_path = Path(temp_dir) / "artifact.out"
        
        console.print(f"  [1] Compiling artifact with definitive harness: [cyan]{DEFINITIVE_HARNESS.name}[/cyan]")
        compile_command = ["gcc", "-fno-stack-protector", "-o", str(executable_path), str(artifact_path), str(DEFINITIVE_HARNESS)]
        
        compile_result = subprocess.run(compile_command, capture_output=True, text=True)
        if compile_result.returncode != 0:
            console.print("[bold red]  ❌ FATAL: Compilation Failed[/bold red]")
            console.print(Panel(compile_result.stderr, title="Compiler Error", border_style="red"))
            raise typer.Exit(code=1)
        console.print("[green]  ✅ Artifact compiled successfully.[/green]")

        payloads = [
            b'This is a completely normal and safe input string.', # Normal Payload
            b'A' * 512                                             # Attack Payload
        ]
        results = []
        console.print("\n  [2] Executing resilience tests...")
        for payload in payloads:
            proc = subprocess.run([str(executable_path)], input=payload, capture_output=True, timeout=5)
            results.append({'outcome': 'survived' if proc.returncode == 0 else 'crashed'})
        
        table = Table(title="Resilience Analysis")
        table.add_column("Payload Type", style="cyan"); table.add_column("Outcome", style="white")
        table.add_row("Normal", results[1]['outcome'])
        table.add_row("Attack", results[0]['outcome'])
        console.print(table)
        
        # The true definition of success for a hardened artifact
        is_hardened = all(r['outcome'] == 'survived' for r in results)
        
        if is_hardened:
            console.rule("[bold green]VALIDATION PASSED[/bold green]")
        else:
            console.rule("[bold red]VALIDATION FAILED[/bold red]")

if __name__ == "__main__":
    app()
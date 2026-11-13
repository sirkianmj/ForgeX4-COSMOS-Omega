#!/usr/bin/env python3
"""COSMOS-Ω Unified CLI - orchestrates the full ForgeX4 pipeline."""
import subprocess
import sys
from pathlib import Path
import typer

app = typer.Typer(help="ForgeX4-COSMOS-Ω Autonomous Security Foundry CLI", no_args_is_help=True)
ROOT = Path(__file__).resolve().parent.parent

@app.command()
def status():
    """Analyze the current project state."""
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "analyze_project_state.py")])

@app.command()
def foundry(target: str = typer.Argument("cjson", help="Target genome name")):
    """Run the Sentinel foundry on a target genome."""
    typer.echo(f"Running Sentinel foundry on target: {target}")
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "run_sentinel_experiment.py")])

@app.command()
def benchmark():
    """Run the assurance benchmark suite."""
    typer.echo("Running assurance benchmark...")
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "run_assurance_benchmark.py")])

@app.command()
def gui():
    """Launch the Flask GUI."""
    typer.echo("Launching ForgeX4 GUI on http://127.0.0.1:5000")
    return subprocess.call([sys.executable, str(ROOT / "app.py")])

if __name__ == "__main__":
    app()

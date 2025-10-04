# Kian Mansouri Jamshidi
#
# File: scripts/analyze_project_state.py
#
# Description:
# A read-only diagnostic tool to scan the COSMOS-Ω project and report on its
# current, factual state. It checks dependencies, key files, data assets,
# and artifacts to provide a trusted baseline for our next steps.

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# --- Setup Project Path ---
# This ensures the script can be run from anywhere and find the project root.
try:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
except NameError:
    # Handle case where script is run in an interactive interpreter
    project_root = Path.cwd()

console = Console()
app = typer.Typer(name="COSMOS-Ω State Analyzer")

def check_path(path: Path, is_dir: bool = False) -> str:
    """Helper to check for file/dir existence and return a formatted string."""
    if path.exists() and (is_dir == path.is_dir()):
        return f"[green]✅ Found[/green]"
    return f"[red]❌ Missing[/red]"

@app.command()
def report():
    """Scans the project and generates a comprehensive state report."""
    
    console.rule("[bold blue]COSMOS-Ω Project State Analysis[/bold blue]")

    # --- Section 1: Inferred Project Stage ---
    console.print(Panel("Stage 1: Project Phase Analysis", title="[bold]Project Stage[/bold]", expand=False))
    stage_evidence = []
    if (project_root / "data/genomes/cjson").exists():
        stage_evidence.append("cJSON target data is present.")
    if (project_root / "artifacts/phase2").exists():
        stage_evidence.append("Phase 2 (Digital Twin) artifacts are present.")
    if (project_root / "scripts/run_assurance_benchmark.py").exists():
        stage_evidence.append("High-Assurance Benchmark script is present.")
    
    if len(stage_evidence) >= 2:
        console.print("EVIDENCE: " + " | ".join(stage_evidence))
        console.print("CONCLUSION: The project is in [bold yellow]Phase 3 (Unassailable Artifact)[/bold yellow], focused on the cJSON target.")
    elif (project_root / "data/genomes/gaia").exists():
        console.print("CONCLUSION: The project is likely in [bold yellow]Phase 1 or 2[/bold yellow], focused on the simpler 'gaia' target.")
    else:
        console.print("[red]CONCLUSION: Critical data or scripts are missing. Unable to determine phase.[/red]")

    # --- Section 2: Dependencies ---
    console.print(Panel("Stage 2: Python Dependencies", title="[bold]Dependencies[/bold]", expand=False))
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        console.print(f"[green]✅ Found 'requirements.txt'.[/green] Contents:")
        with open(req_path, 'r') as f:
            console.print(f"[cyan]{f.read()}[/cyan]")
    else:
        console.print("[red]❌ 'requirements.txt' is missing. Dependencies are unknown.[/red]")

    # --- Section 3: Key Files and Entry Points ---
    console.print(Panel("Stage 3: Key Scripts & Library Files", title="[bold]Key Files[/bold]", expand=False))
    table = Table(title="File Status")
    table.add_column("Category", style="cyan")
    table.add_column("File Path", style="white")
    table.add_column("Status", style="magenta")

    # Key Scripts
    table.add_row("Entry Point", "scripts/cosmos_cli.py", check_path(project_root / "scripts/cosmos_cli.py"))
    table.add_row("Entry Point", "scripts/run_arms_race.py", check_path(project_root / "scripts/run_arms_race.py"))
    table.add_row("Entry Point", "scripts/run_assurance_benchmark.py", check_path(project_root / "scripts/run_assurance_benchmark.py"))
    
    # Core Library
    table.add_row("Core Library", "cosmos/parser/parser.py", check_path(project_root / "cosmos/parser/parser.py"))
    table.add_row("Core Library", "cosmos/foundry/foundry.py", check_path(project_root / "cosmos/foundry/foundry.py"))
    table.add_row("Core Library", "cosmos/foundry/titans.py", check_path(project_root / "cosmos/foundry/titans.py"))
    table.add_row("Core Library", "cosmos/foundry/fitness.py", check_path(project_root / "cosmos/foundry/fitness.py"))

    console.print(table)

    # --- Section 4: Data Assets ---
    console.print(Panel("Stage 4: Data & Genome Analysis", title="[bold]Data Assets[/bold]", expand=False))
    data_table = Table(title="Data Status")
    data_table.add_column("Asset Type", style="cyan")
    data_table.add_column("Asset Name", style="white")
    data_table.add_column("Status", style="magenta")

    # Genomes
    genomes_dir = project_root / "data/genomes"
    data_table.add_row("Target Genome", "cJSON", check_path(genomes_dir / "cjson", is_dir=True))
    data_table.add_row("Target Genome", "Gaia (Simple)", check_path(genomes_dir / "gaia", is_dir=True))
    data_table.add_row("Attacker Genome", "Uranus", check_path(genomes_dir / "uranus", is_dir=True))
    # Telemetry
    data_table.add_row("Telemetry Data", "telemetry_v2", check_path(project_root / "data/telemetry_v2", is_dir=True))
    
    console.print(data_table)

    # --- Section 5: Artifacts ---
    console.print(Panel("Stage 5: Build & Run Artifacts", title="[bold]Artifacts[/bold]", expand=False))
    artifacts_table = Table(title="Artifact Status")
    artifacts_table.add_column("Artifact Type", style="cyan")
    artifacts_table.add_column("Artifact Name", style="white")
    artifacts_table.add_column("Status", style="magenta")
    
    artifacts_dir = project_root / "artifacts"
    artifacts_table.add_row("Phase 1 Output", "Phase 1 Champion", check_path(artifacts_dir / "phase1/champion_v0.1.c"))
    artifacts_table.add_row("Phase 2 Output", "Digital Twin Model", check_path(artifacts_dir / "phase2/digital_twin_v5.3_hybrid_ensemble", is_dir=True))
    artifacts_table.add_row("Latest Champion", "Aegis Sentinel v1", check_path(artifacts_dir / "aegis_sentinel_v1.c"))

    console.print(artifacts_table)
    console.rule("[bold blue]Analysis Complete[/bold blue]")

if __name__ == "__main__":
    app()
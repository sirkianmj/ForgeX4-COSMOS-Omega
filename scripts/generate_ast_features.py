# Kian Mansouri Jamshidi
#
# File: scripts/generate_static_features.py
#
# Description:
# [DEFINITIVE - FIREBREAK V2] This utility performs the one-time, fragile
# parse of a C file and saves its static AST features to a JSON file.
# This creates the "data firebreak" for our main engine.

import sys
import json
from pathlib import Path
import typer
from rich.console import Console

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from cosmos.parser.parser import CParser
from cosmos.foundry.feature_extractor import AstFeatureVisitor

app = typer.Typer(name="COSMOS-Ω Static Feature Generator")
console = Console()

TARGET_FILE = project_root / "data/genomes/cjson/cJSON.c"
OUTPUT_FILE = project_root / "artifacts/cjson_static_features.json"

@app.command()
def run():
    """Parses the target C file and saves its AST features."""
    console.rule("[bold blue]Initiating One-Time Static Feature Extraction[/bold blue]")
    try:
        parser = CParser()
        console.print(f"  [1] Parsing target: [cyan]{TARGET_FILE.name}[/cyan]")
        ast = parser.parse_file(str(TARGET_FILE))
        
        console.print("  [2] Extracting features...")
        visitor = AstFeatureVisitor()
        features = visitor.extract(ast)
        
        console.print(f"  [3] Saving features to: [cyan]{OUTPUT_FILE.name}[/cyan]")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(features, f, indent=4)
            
        console.rule("[bold green]SUCCESS[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]FATAL ERROR[/bold red]"); console.print(e)

if __name__ == "__main__":
    app()
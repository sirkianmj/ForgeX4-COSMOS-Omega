# Kian Mansouri Jamshidi
#
# File: scripts/generate_lexical_features.py
#
# Description:
# [DEFINITIVE - FIREBREAK V3] This is the correct, one-time utility.
# It correctly imports and runs the 'extract_lexical_features' function
# to create our static data artifact.

import sys
import json
from pathlib import Path
import typer
from rich.console import Console

# --- Setup Project Path ---
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Correctly import the logic from the library file you created
from cosmos.foundry.feature_extractor_lexical import extract_lexical_features

app = typer.Typer(name="COSMOS-Ω Lexical Feature Generator")
console = Console()

TARGET_FILE = project_root / "data/genomes/cjson/cJSON.c"
# The definitive output path
OUTPUT_FILE = project_root / "artifacts/cjson_lexical_features.json"

@app.command()
def generate():
    """Parses the target C file and saves its lexical features to a JSON file."""
    console.rule("[bold blue]Initiating One-Time Lexical Feature Extraction[/bold blue]")
    try:
        console.print(f"  [1] Reading target file: [cyan]{TARGET_FILE.name}[/cyan]")
        with open(TARGET_FILE, 'r') as f:
            source_code = f.read()
        
        console.print(f"  [2] Extracting lexical features...")
        features = extract_lexical_features(source_code)
        
        console.print(f"  [3] Saving features to JSON: [cyan]{OUTPUT_FILE.name}[/cyan]")
        OUTPUT_FILE.parent.mkdir(exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(features, f, indent=4)
            
        console.rule("[bold green]SUCCESS[/bold green]")
        console.print("The static lexical features have been successfully generated and saved.")

    except Exception as e:
        console.print(f"\n[bold red]A FATAL ERROR OCCURRED[/bold red]"); console.print(e)

if __name__ == "__main__":
    app()
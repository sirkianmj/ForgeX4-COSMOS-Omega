#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: cosmos/foundry/fitness.py
# Date: 2025-09-25
#
# Description:
# Implements the "Crucible" fitness function.
#
import subprocess
import os
import uuid
import copy
from pycparser import c_ast
from cosmos.parser import parser

# --- Configuration ---  <-- THIS BLOCK WAS MISSING
CRONOS_SOURCE_PATH = "data/genomes/cronos/cronos_v0.1.c"
ATTACK_PAYLOAD = b"A" * 32 + b"\n"

FITNESS_CRASH = -10.0
FITNESS_SURVIVE = 100.0
FITNESS_COMPILE_FAIL = -1000.0
# --- END OF MISSING BLOCK ---

def evaluate_fitness(genome_ast: c_ast.FileAST) -> float:
    """
    Evaluates the fitness of a single genome (AST).
    """
    run_id = str(uuid.uuid4())
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    gaia_source_path = os.path.join(temp_dir, f"gaia_{run_id}.c")
    output_binary_path = os.path.join(temp_dir, f"app_{run_id}")
    
    compile_failed = False

    try:
        # Step 1: Make a copy to avoid corrupting the main population's AST
        ast_to_compile = copy.deepcopy(genome_ast)

        # Step 2: Clean the AST to remove all typedefs from pycparser's fake headers
        ast_to_compile.ext = [node for node in ast_to_compile.ext if not isinstance(node, c_ast.Typedef)]

        # Step 3: Un-parse the clean AST and add the REAL system headers
        headers = '#include <stdio.h>\n#include <string.h>\n\n'
        gaia_code = headers + parser.unparse_ast_to_c(ast_to_compile)
        
        with open(gaia_source_path, "w") as f:
            f.write(gaia_code)

        # Step 4: Compile
        compile_command = [
            "riscv64-linux-gnu-gcc", "-static", "-o", output_binary_path,
            gaia_source_path, CRONOS_SOURCE_PATH
        ]
        
        compile_process = subprocess.run(
            compile_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=15
        )

        if compile_process.returncode != 0:
            compile_failed = True
            print(f"  - Compile FAILED. Compiler Output:\n---\n{compile_process.stdout}\n---")
            return FITNESS_COMPILE_FAIL

        # Step 5: Run the compiled binary
        run_command = ["qemu-riscv64-static", output_binary_path]
        run_process = subprocess.run(
            run_command, input=ATTACK_PAYLOAD,
            capture_output=True, timeout=5
        )

        if run_process.returncode < 0:
            return FITNESS_CRASH
        else:
            return FITNESS_SURVIVE

    except Exception as e:
        print(f"  - An unexpected Python error occurred: {e}")
        compile_failed = True
        return FITNESS_COMPILE_FAIL
    finally:
        # Step 6: Clean up
        if not compile_failed:
            if os.path.exists(gaia_source_path):
                os.remove(gaia_source_path)
            if os.path.exists(output_binary_path):
                os.remove(output_binary_path)
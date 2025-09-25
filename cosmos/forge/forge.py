#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: cosmos/forge/forge.py
# Date: 2025-09-25
#
# Description:
# This module, The Forge, is responsible for the final step of the pipeline:
# taking a champion AST genome and forging it into a deployable artifact,
# in this case, a compilable C source file.
#
import os
from pycparser import c_ast
from cosmos.parser import parser

def forge_champion(champion_ast: c_ast.FileAST, output_path: str):
    """
    Un-parses a champion AST and saves it as a C source file.

    Args:
        champion_ast (c_ast.FileAST): The AST of the best-performing genome.
        output_path (str): The file path to save the C code to.
    """
    print(f"\n--- Forging Champion ---")
    if champion_ast is None:
        print("ERROR: Champion genome is None. Cannot forge artifact.")
        return

    try:
        # Step 1: Clean the final AST to remove parser artifacts
        ast_to_forge = copy.deepcopy(champion_ast)
        ast_to_forge.ext = [node for node in ast_to_forge.ext if not isinstance(node, c_ast.Typedef)]

        # Step 2: Un-parse the clean AST and add system headers
        headers = '#include <stdio.h>\n#include <string.h>\n\n'
        champion_code = headers + parser.unparse_ast_to_c(ast_to_forge)

        # Step 3: Save the final C code to the specified file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(champion_code)
        
        print(f"SUCCESS: Champion artifact forged successfully.")
        print(f"Saved to: {output_path}")

    except Exception as e:
        print(f"ERROR: An error occurred during forging: {e}")

# We need to import copy for the deepcopy operation
import copy
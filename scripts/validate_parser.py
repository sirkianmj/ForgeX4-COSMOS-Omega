#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: scripts/validate_parser.py
# Date: 2025-09-25
#
# Description:
# A simple script to validate the core functionality of the parser module.
# It parses a C file into an AST, prints a confirmation, and then un-parses
# the AST back into C code, printing the result to the console.
#
import os
import sys

# This is a common Python pattern to allow the script to find our main 'cosmos'
# package, even though we are running it from the 'scripts' directory.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cosmos.parser import parser

# --- Configuration ---
# The target C file we want to test our parser on.
TARGET_C_FILE = "data/genomes/gaia/gaia_v0.1.c"

def main():
    """Main validation function."""
    print("--- Parser Validation Script ---")
    
    # Construct the full path to the C file from the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, TARGET_C_FILE)
    
    if not os.path.exists(file_path):
        print(f"ERROR: Cannot find target file: {file_path}")
        return

    print(f"1. Attempting to parse '{file_path}' into an AST...")
    
    try:
        # Call our parsing function
        gaia_ast = parser.parse_c_file_to_ast(file_path)
        print("   SUCCESS: AST generated successfully.")
        # The AST object itself is a complex tree. For validation, we can just
        # show a small part of it, like the number of top-level nodes.
        print(f"   AST contains {len(gaia_ast.ext)} top-level declarations.")

        print("\n2. Attempting to un-parse the AST back to C code...")
        
        # Call our un-parsing function
        regenerated_code = parser.unparse_ast_to_c(gaia_ast)
        
        print("   SUCCESS: C code regenerated.")
        print("--- Regenerated Code ---")
        print(regenerated_code)
        print("------------------------")
        print("\nValidation Complete. The parser can successfully perform a round-trip.")

    except Exception as e:
        print(f"\nVALIDATION FAILED: An error occurred during the process.")
        # The parser functions already print detailed errors, so we don't need to repeat.

if __name__ == '__main__':
    main()
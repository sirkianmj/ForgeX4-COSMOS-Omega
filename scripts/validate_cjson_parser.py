# scripts/validate_cjson_parser.py

import sys
import os
import traceback

# Add the project root to the Python path to allow for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from cosmos.parser.parser import CParser

def main():
    """
    Validates that the CParser can successfully parse the cJSON source code.
    """
    print("--- CParser Validation for cJSON ---")
    
    cjson_source_path = os.path.join(project_root, 'data', 'genomes', 'cjson', 'cJSON.c')
    
    if not os.path.exists(cjson_source_path):
        print(f"\n[ERROR] Source file not found: {cjson_source_path}")
        return

    print(f"Attempting to parse: {cjson_source_path}")

    try:
        parser = CParser()
        ast = parser.parse_file(cjson_source_path, cpp_args=[r'-Idata/genomes/cjson'])
        
        print("\n[SUCCESS] cJSON source code parsed successfully.")
        
        if ast and hasattr(ast, 'ext'):
            print(f"AST generated with {len(ast.ext)} external declarations (functions, globals, etc.).")

    except Exception:
        print("\n[FAILURE] An error occurred during parsing.")
        print("-" * 50)
        traceback.print_exc()
        print("-" * 50)

if __name__ == "__main__":
    main()
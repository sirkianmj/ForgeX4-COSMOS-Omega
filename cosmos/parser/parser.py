#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: cosmos/parser/parser.py
# Date: 2025-09-25
#
# Description:
# This module is responsible for the critical task of converting C source code
# into a mutable Abstract Syntax Tree (AST) representation, and vice-versa.
# This is the core of the "Code-as-Data" paradigm for the foundry.
#
import os
import subprocess
import pycparser # <-- ADDED
from pycparser import c_parser, c_ast
from pycparser.c_generator import CGenerator

def clean_ast(ast: c_ast.FileAST):
    """
    Removes all top-level Typedef nodes from an AST.
    This is used to strip out the fake libc typedefs before compilation.
    """
    ast.ext = [node for node in ast.ext if not isinstance(node, c_ast.Typedef)]

def get_pycparser_fake_libc_path() -> str:
    """Finds the path to the fake libc headers provided by pycparser."""
    pycparser_path = os.path.dirname(pycparser.__file__)
    return os.path.join(pycparser_path, 'utils', 'fake_libc_include')


def parse_c_file_to_ast(c_file_path: str) -> c_ast.FileAST:
    """
    Parses a C source file into a pycparser AST object.

    This function orchestrates the two-step process required by pycparser:
    1. Pre-processes the C file using gcc -E to handle includes/macros.
    2. Parses the resulting pure C code into an AST.

    Args:
        c_file_path (str): The full path to the C source file.

    Returns:
        c_ast.FileAST: The root of the Abstract Syntax Tree.
    """
    try:
        # Step 1: Pre-process the C file using gcc with fake headers
        fake_libc_path = get_pycparser_fake_libc_path()

        # This command is now more specific.
        # -nostdinc: Don't search the standard system directories for header files.
        # -I<path>: Add the fake libc path to the list of directories to be searched.
        preprocessed_command = [
            "gcc",
            "-E",
            "-nostdinc",
            f"-I{fake_libc_path}",
            c_file_path,
        ]
        
        preprocessed_text = subprocess.check_output(preprocessed_command, text=True)

        # Step 2: Parse the pre-processed code
        parser = c_parser.CParser()
        ast = parser.parse(preprocessed_text, filename=c_file_path)
        return ast

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to pre-process C file: {c_file_path}")
        print(f"GCC Error: {e.stderr}")
        raise
    except Exception as e:
        print(f"ERROR: Failed to parse C file: {c_file_path}")
        print(f"Parser Error: {e}")
        raise

def unparse_ast_to_c(ast: c_ast.FileAST) -> str:
    """
    Converts a pycparser AST object back into a string of C source code.

    Args:
        ast (c_ast.FileAST): The AST to be un-parsed.

    Returns:
        str: A string containing the compilable C code.
    """
    generator = CGenerator()
    return generator.visit(ast)
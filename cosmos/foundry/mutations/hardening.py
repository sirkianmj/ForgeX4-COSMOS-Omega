#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: cosmos/foundry/mutations/hardening.py
# Date: 2025-09-25
#
# Description:
# This definitive version uses a robust, generic recursive transformation
# with detailed error logging to be completely transparent.
#

import copy
from pycparser import c_ast

def _recursive_transform(node):
    """
    Recursively traverses the AST, rebuilding it with transformations.
    """
    if not isinstance(node, (c_ast.Node, list)):
        return node

    if isinstance(node, list):
        return [_recursive_transform(item) for item in node]

    # --- Core transformation logic for 'gets' ---
    if isinstance(node, c_ast.FuncCall) and isinstance(node.name, c_ast.ID) and node.name.name == 'gets':
        print("   MUTATION: Found and transformed `gets()` call.")
        buffer_node = node.args.exprs[0]
        return c_ast.FuncCall(
            name=c_ast.ID('fgets'),
            args=c_ast.ExprList(exprs=[
                buffer_node,
                c_ast.UnaryOp(op='sizeof', expr=buffer_node),
                c_ast.ID('stdin')
            ])
        )

    # --- THIS IS THE DEFINITIVE, INSTRUMENTED RECONSTRUCTION LOGIC ---
    
    # The constructor arguments are the node's slots.
    constructor_args = node.__slots__
    
    # Build a dictionary of keyword arguments for the new node's constructor.
    kwargs = {}
    for attr_name in constructor_args:
        # We cannot pass internal attributes to the constructor.
        if attr_name.startswith('__'):
            continue
            
        attr_value = getattr(node, attr_name)
        # Recursively transform the attribute's value.
        kwargs[attr_name] = _recursive_transform(attr_value)

    # Try to reconstruct the node. If it fails, log everything.
    try:
        return type(node)(**kwargs)
    except Exception as e:
        print("\n--- FATAL RECONSTRUCTION ERROR ---")
        print(f"Failed to reconstruct node of type: {type(node).__name__}")
        print(f"Constructor expects slots: {node.__slots__}")
        print(f"Provided kwargs: {kwargs.keys()}")
        print(f"Error: {e}")
        print("------------------------------------")
        # Re-raise the exception to halt execution, since this is a fatal bug.
        raise


def mutate_gets_to_fgets(ast: c_ast.FileAST) -> c_ast.FileAST:
    """
    Applies the gets-to-fgets mutation to an entire AST by creating a
    new, transformed version of the AST.
    """
    ast_copy = copy.deepcopy(ast)
    new_ast = _recursive_transform(ast_copy)
    return new_ast
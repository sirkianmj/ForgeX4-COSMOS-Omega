#
# ForgeX4 COSMOS-Ω
#
# Author: Kian Mansouri Jamshidi
# Project Director: Kian Mansouri Jamshidi
#
# File: cosmos/foundry/mutations/hardening.py
# Date: 2024-05-24
#
# Description:
# This module contains the genetic operators for "hardening" a C-code AST.
# This version uses the more fundamental NodeVisitor to bypass a persistent
# ImportError related to NodeTransformer in the pycparser library.
#

from pycparser import c_ast

class GetsToFgetsVisitor(c_ast.NodeVisitor):
    """
    An AST NodeVisitor that finds calls to `gets()` and manually replaces
    the node in the AST with a call to `fgets()`.
    """
    def visit_FuncCall(self, node):
        # We are only interested in function calls where the function name is 'gets'.
        if isinstance(node.name, c_ast.ID) and node.name.name == 'gets':
            print("   MUTATION: Found a `gets()` call. Transforming to `fgets()`.")

            # The argument to gets() is the buffer we want to protect.
            buffer_node = node.args.exprs[0]

            # We construct a new AST node representing:
            # fgets(buffer, sizeof(buffer), stdin)
            new_node = c_ast.FuncCall(
                name=c_ast.ID('fgets'),
                args=c_ast.ExprList(exprs=[
                    buffer_node,
                    c_ast.UnaryOp(op='sizeof', expr=buffer_node),
                    c_ast.ID('stdin')
                ])
            )

            # This is the key difference from NodeTransformer.
            # We are not returning the new node. We must manually replace the
            # old node with the new one. Since we don't have a reference to the
            # parent node here, we will simply copy the contents of the new
            # node into the old one. This is a common and effective technique.
            for attr in new_node.attr_names:
                setattr(node, attr, getattr(new_node, attr))
            node.coord = new_node.coord
            
        # Continue visiting children nodes
        self.generic_visit(node)


def mutate_gets_to_fgets(ast: c_ast.FileAST) -> c_ast.FileAST:
    """
    Applies the gets-to-fgets mutation to an entire AST.

    Args:
        ast (c_ast.FileAST): The source AST to mutate.

    Returns:
        c_ast.FileAST: The modified AST.
    """
    visitor = GetsToFgetsVisitor()
    visitor.visit(ast)
    return ast
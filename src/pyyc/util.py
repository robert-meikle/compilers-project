import ast
import os
from ast import FunctionDef, Call, Name, arguments, AST


def add_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree


class RemoveIntCasts(ast.NodeTransformer):
    def visit_Call(self, node: Call):
        if isinstance(node.func, Name) and node.func.id == "int":
            return node.args[0]
        return node


def create_ast(path: str):
    """
    Reads the input python program and creates an AST.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"'{path}' does not correspond to a valid file.")

    prog = ""
    with open(path, "r", encoding="utf-8") as file_:
        prog = file_.read()

    # Switched back to using default parser after Assignment 2.
    # lexer = lex.lex(module=lexer_rules)
    # parser = yacc.yacc(module=parser_rules)
    # return parser.parse(prog, lexer=lexer)

    return ast.parse(prog)


def get_function_defs(_ast: AST):
    """
    Iterate over the global scope and collect all of the function defs.
    """
    main = FunctionDef("main", args=arguments(args=[]), body=[])
    func_defs = [main]

    for node in _ast.body:
        if isinstance(node, FunctionDef):
            func_defs.append(node)
        else:
            main.body.append(node)
    return func_defs

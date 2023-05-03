import ast
import logging
from ast import (
    Assign,
    Constant,
    FunctionDef,
    Index,
    List,
    Load,
    Name,
    Store,
    Subscript,
    AST,
)


class FreeVars(ast.NodeVisitor):
    global_keywords = {"print", "int", "eval", "input"}

    def __init__(self):
        self.used_vars = set()
        self.bound_vars = set()

    def visit_FunctionDef(self, node: FunctionDef):
        self.generic_visit(node)
        for arg_obj in node.args.args:
            self.bound_vars.add(arg_obj.arg)

    def visit_Name(self, node):
        if node.id not in ["True", "False"] and node.id not in self.global_keywords:
            if isinstance(node.ctx, Load):
                self.used_vars.add(node.id)
            elif isinstance(node.ctx, Store):
                self.bound_vars.add(node.id)


def get_free(ast_: AST):
    global_keywords = {"print", "int", "eval", "input"}
    used_vars = set()
    bound_vars = set()
    for node in ast.walk(ast_):
        if isinstance(node, FunctionDef):
            for arg_obj in node.args.args:
                bound_vars.add(arg_obj.arg)
        elif isinstance(node, Name):
            if node.id not in ["True", "False"] and node.id not in global_keywords:
                if isinstance(node.ctx, Load):
                    used_vars.add(node.id)
                elif isinstance(node.ctx, Store):
                    bound_vars.add(node.id)

    return used_vars, bound_vars


def compute_free_vars(ast_):
    # get all function names
    func_names = set()
    for node in ast.walk(ast_):
        if isinstance(node, FunctionDef):
            func_names.add(node.name)
    logging.info("\nFunction Names: %s", func_names)
    logging.info("\nFree Vars")
    for node in ast.walk(ast_):
        if isinstance(node, FunctionDef):
            used, bound = get_free(node)
            used = used - func_names
            node.free_vars = list(used - bound - func_names)
            logging.info(
                "\nFunction %s:\n\tused: %s\n\tbound: %s\n\tfree: %s",
                node.name,
                used,
                bound,
                node.free_vars,
            )

    return ast_


class Heapifier(ast.NodeTransformer):
    def __init__(self, marked):
        self.to_heapify = marked

    def visit_Assign(self, node):
        self.generic_visit(node)
        if isinstance(node.targets[0], Name):
            if node.targets[0].id in self.to_heapify:
                return Assign(node.targets, List(elts=[node.value], ctx=Load()))
        return node

    def visit_Name(self, node):
        if node.id in self.to_heapify and isinstance(node.ctx, Load):
            return Subscript(node, Index(Constant(0)), ctx=Load())
        return node


def heapify(ast_):
    ast_ = compute_free_vars(ast_)
    return ast_
    # heapifier = Heapifier(marked)
    # return ast.fix_missing_locations(heapifier.visit(ast_))

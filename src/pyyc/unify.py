import ast
from ast import FunctionDef, Load, Module, Name, Return


class Unify(ast.NodeTransformer):
    def get_name(self):
        name = f"lambda_{self.lambda_count}"
        self.lambda_count += 1
        return name

    def __init__(self):
        self.lambda_count = 0
        self.defs_to_insert: list[tuple(list, FunctionDef)] = []
        self.changed = False
        self.current_scope = None

    def visit_Module(self, node: Module):
        self.current_scope = node.body
        self.generic_visit(node)
        return node

    def visit_Lambda(self, node):
        old_scope = self.current_scope
        new_func_def = FunctionDef(
            name=self.get_name(),
            args=node.args,
            body=[],
            decorator_list=[],
            returns=None,
        )
        self.current_scope = new_func_def.body
        self.generic_visit(node)
        new_func_def.body.append(Return(node.body))

        self.current_scope = old_scope
        self.defs_to_insert.append((self.current_scope, new_func_def))
        return Name(id=new_func_def.name, ctx=Load())


def unify_func_lambda(ast_):
    unifier = Unify()

    ast_ = unifier.visit(ast_)

    for new_def in unifier.defs_to_insert:
        new_def[0].insert(0, new_def[1])

    return ast.fix_missing_locations(ast_)

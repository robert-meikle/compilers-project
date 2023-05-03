import ast
from ast import (
    Assign,
    Call,
    Constant,
    FunctionDef,
    List,
    Load,
    Name,
    Store,
    Subscript,
    arg,
)

builtin_names = {
    "is_int",
    "is_bool",
    "is_big",
    "is_function",
    "is_object",
    "is_class",
    "is_unbound_method",
    "is_bound_method",
    "inject_int",
    "inject_bool",
    "inject_big",
    "project_int",
    "project_bool",
    "project_big",
    "is_true",
    "print_any",
    "input_int",
    "input_pyobj",
    "eval_pyobj",
    "eval_input_pyobj",
    "create_list",
    "create_dict",
    "set_subscript",
    "get_subscript",
    "add",
    "equal",
    "not_equal",
    "create_closure",
    "get_fun_ptr",
    "get_free_vars",
    "set_free_vars",
    "error_pyobj",
    "print",
    "int",
    "eval",
    "input",
}


class ClosureConverter(ast.NodeTransformer):
    def get_closure_name(self):
        name = f"closure_{self.closure_count}"
        self.closure_count += 1
        return name

    def __init__(self):
        self.defs = []
        self.closure_count = 0

    def visit_FunctionDef(self, node: FunctionDef):
        self.generic_visit(node)

        free_vars_list = Name(f"free_vars_{node.name}", ctx=Load())
        vars_argument = List([], ctx=Load())
        for i, var in enumerate(node.free_vars):
            node.body.insert(
                0,
                Assign(
                    [Name(var, ctx=Store())],
                    value=Subscript(free_vars_list, Constant(i), ctx=Load()),
                ),
            )
            vars_argument.elts.insert(0, Name(var))
        func_name = node.name
        node.name = self.get_closure_name()
        node.args.args.insert(0, arg(free_vars_list.id, annotation=None))
        self.defs.append(node)

        return Assign(
            targets=[Name(id=func_name, ctx=Store())],
            value=Call(
                func=Name("create_closure", ctx=Load()),
                args=[Name(id=node.name, ctx=Load()), vars_argument],
                keywords=[],
            ),
        )

    def visit_Call(self, node):
        self.generic_visit(node)
        # check if function is a runtime function
        if isinstance(node.func, Name) and node.func.id in builtin_names:
            return node
        else:
            return Call(
                func=Call(
                    Name("get_fun_ptr", ctx=Load()),
                    args=[
                        Call(
                            Name("inject_big", ctx=Load()),
                            args=[node.func],
                            keywords=[],
                        )
                    ],
                    keywords=[],
                ),
                args=[
                    Call(
                        func=Name("get_free_vars", ctx=Load()),
                        args=[
                            Call(
                                Name("inject_big", ctx=Load()),
                                args=[node.func],
                                keywords=[],
                            )
                        ],
                        keywords=[],
                    )
                ]
                + node.args,
                keywords=[],
            )


def closure(ast_):
    converter = ClosureConverter()
    ast_ = converter.visit(ast_)

    # insert defs at the top of ast
    for def_ in converter.defs:
        ast_.body.insert(0, def_)

    return ast.fix_missing_locations(ast_)

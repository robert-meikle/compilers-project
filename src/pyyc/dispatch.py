from _ast import AnnAssign, BinOp, Call, Compare
import ast
from ast import *
from typing import Any
from pytypes import *

class Dispatcher(ast.NodeTransformer):
    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        self.generic_visit(node)
        if isinstance(node.value, List):
            print(node.annotation.slice.id)
            # assign to create_list
            new_body = [
                Assign(
                    targets=[node.target],
                    value=Call(
                        func=Name("inject_big", Load()),
                        args=[
                            Call(
                                func=Name("create_list", Load()),
                                args=[
                                    Call(
                                        func=Name("inject_int", Load()),
                                        args=[Constant(len(node.value.elts))],
                                        keywords=[],
                                    )
                                ],
                                keywords=[],
                            )
                        ],
                        keywords=[],
                    ),
                )
            ]
            # populate list
            for i, val in enumerate(node.value.elts):
                inject_val_func = "inject_"
                match node.annotation.slice.id:
                    case "int": 
                        inject_val_func = "inject_int"
                    case "bool":
                        inject_val_func = "inject_bool"
                    case _:
                        raise NotImplementedError("unimplemented list eliment type: ",node.annotation.slice.id)
                new_body.append(
                    Expr(
                        value=Call(
                            func=Name("set_subscript", Load()),
                            args=[
                                node.target,
                                Call(
                                    func=Name("inject_int", Load()),
                                    args=[Constant(i)],
                                    keywords=[],
                                ),
                                Call(
                                    func=Name(inject_val_func, Load()),
                                    args=[val],
                                    keywords=[],
                                )
                            ],
                            keywords=[],
                        )
                    )
                )
            return new_body
        return Assign(targets=[node.target], value=node.value)

    def visit_Call(self, node: Call) -> Any:
        self.generic_visit(node)
        if isinstance(node.func, Name):
            if node.func.id == "print":
                if isinstance(node.type_, PyInt):
                    node.func.id = "print_int_nl"
                elif isinstance(node.type_, PyBool):
                    node.func.id = "print_bool_nl"
                    #node.args[0] = Call(func=Name("inject_bool", ctx=Load()), args=[node.args[0]], keywords=[])
            if node.func.id == "int":
                print("test")
                if (
                    isinstance(node.args[0], Call)
                    and isinstance(node.args[0].func, Name)
                    and node.args[0].func.id == "input"
                ):
                    return Call(
                        func=Name("input_static", ctx=Load()), args=[], keywords=[]
                    )
        return node

    def visit_BinOp(self, node: BinOp) -> Any:
        self.generic_visit(node)
        if isinstance(node.type_, PyInt):
            return node
        elif isinstance(node.type_, PyList):
            return Call(
                func=Name("inject_big", ctx=Load()),
                args=[
                    Call(
                        func=Name("add", ctx=Load()),
                        args=[
                            Call(
                                func=Name("project_big", ctx=Load()),
                                args=[node.left],
                                keywords=[],
                            ),
                            Call(
                                func=Name("project_big", ctx=Load()),
                                args=[node.right],
                                keywords=[],
                            ),
                        ],
                        keywords=[],
                    )
                ],
                keywords=[],
            )
        else:
            raise NotImplementedError("Binop unhandled case, shouldn't happen")

    def visit_Compare(self, node: Compare) -> Any:
        self.generic_visit(node)
        # assume only 2 operands
        # for Is, convert to false, if different types, if same type convert to Eq
        if isinstance(node.ops[0], Is):
            if node.types_[0] != node.types_[1]:
                return Constant(value=0)
            node.ops[0] = Eq()
        if isinstance(node.ops[0], Eq):
            if node.types_[0] != node.types_[1]:
                if isinstance(node.types_[0], (PyList, PyDict)) or isinstance(node.types_[1], (PyList, PyDict)):
                    return Constant(value=0)
            elif isinstance(node.types_[0], (PyList, PyDict)):
                return Call(
                    func=Name("equal", ctx=Load()),
                    args=[
                        Call(
                            func=Name("project_big", ctx=Load()),
                            args=[node.left],
                            keywords=[],
                        ),
                        Call(
                            func=Name("project_big", ctx=Load()),
                            args=[node.comparators[0]],
                            keywords=[],
                        ),
                    ],
                    keywords=[],
                )
            return node
        elif isinstance(node.ops[0], NotEq):
            if node.types_[0] != node.types_[1]:
                if isinstance(node.types_[0], (PyList, PyDict)) or isinstance(node.types_[1], (PyList, PyDict)):
                    return Constant(value=0)
            elif isinstance(node.types_[0], (PyList, PyDict)):
                return Call(
                    func=Name("not_equal", ctx=Load()),
                    args=[
                        Call(
                            func=Name("project_big", ctx=Load()),
                            args=[node.left],
                            keywords=[],
                        ),
                        Call(
                            func=Name("project_big", ctx=Load()),
                            args=[node.comparators[0]],
                            keywords=[],
                        ),
                    ],
                    keywords=[],
                )
            return node
        return node

    def visit_Constant(self, node):
        if node.value == True: node.value = 1
        elif node.value == False: node.value = 0
        return node


def dispatch(ast_: AST):
    d = Dispatcher()
    return ast.fix_missing_locations(d.visit(ast_))

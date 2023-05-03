from _ast import AnnAssign, BinOp
import ast
from ast import *
from typing import Any
from pytypes import *


class Dispatcher(ast.NodeTransformer):
    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        if isinstance(node.value, List):
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
                                val,
                            ],
                            keywords=[],
                        )
                    )
                )
            return new_body

    def visit_BinOp(self, node: BinOp) -> Any:
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


def dispatch(ast_: AST):
    d = Dispatcher()
    return ast.fix_missing_locations(d.visit(ast_))

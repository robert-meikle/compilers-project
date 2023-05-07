from _ast import AnnAssign, BinOp, Call, Compare
import ast
from ast import *
from typing import Any
from pytypes import *


class Dispatcher(ast.NodeTransformer):
    def visit_Assign(self, node):
        self.generic_visit(node)
        # needed for list definitions created by flattening
        if isinstance(node.value, List):
            # try to detect list element type, else default to int
            el_type = "int"
            if len(node.value.elts) > 0 and isinstance(node.value.elts[0], Constant):
                el_type = type(node.value.elts[0].value).__name__
            # assign to create_list
            new_body = [
                Assign(
                    targets=node.targets,
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
                # for lists and dicts call normally, else need to inject
                val_func = None
                if isinstance(val, (List, Dict)):
                    val_func = val
                else:
                    val_func = Call(
                        func=Name(f"inject_{el_type}", Load()),
                        args=[val],
                        keywords=[],
                    )
                new_body.append(
                    Expr(
                        value=Call(
                            func=Name("set_subscript", Load()),
                            args=[
                                node.targets[0],
                                Call(
                                    func=Name("inject_int", Load()),
                                    args=[Constant(i)],
                                    keywords=[],
                                ),
                                val_func,
                            ],
                            keywords=[],
                        )
                    )
                )
            return new_body

        if isinstance(node.value, Dict):
            # try to detect dict key/val type, else default to int
            key_type = "int"
            val_type = "int"
            # can detect nested dicts here
            if (hasattr(node,"type_")):
                if str(node.type_.val_type)!="int":
                    val_type = "big"
            if len(node.value.keys) > 0 and isinstance(node.value.keys[0], Constant):
                el_type = type(node.value.keys[0].value).__name__
                if isinstance(node.value.values[0], Constant):
                    val_type = type(node.value.values[0].value).__name__
            # assign to create_list
            new_body = [
                Assign(
                    targets=node.targets,
                    value=Call(
                        func=Name("inject_big", Load()),
                        args=[
                            Call(
                                func=Name("create_dict", Load()),
                                args=[],
                                keywords=[],
                            )
                        ],
                        keywords=[],
                    ),
                )
            ]
            # populate list
            for i, (key, val) in enumerate(zip(node.value.keys, node.value.values)):
                # for lists and dicts call normally, else need to inject
                val_func = None
                if isinstance(val, List):
                    val_func = val
                    key_func = key
                else:
                    if val_type != "big":
                        val_func = Call(
                            func=Name(f"inject_{val_type}", Load()),
                            args=[val],
                            keywords=[],
                        )
                    else:
                        val_func = val
                    key_func = Call(
                        func=Name(f"inject_{key_type}", Load()),
                        args=[key],
                        keywords=[],
                    )
                new_body.append(
                    Expr(
                        value=Call(
                            func=Name("set_subscript", Load()),
                            args=[
                                node.targets[0],
                                key_func,
                                val_func,
                            ],
                            keywords=[],
                        )
                    )
                )
            return new_body
        # for assignments to subscripts
        if isinstance(node.targets[0], Subscript):
            # for lists and dicts call normally, else need to inject
            val_func = None
            if isinstance(node.value, (List, Dict)):
                val_func = node.value
            else:
                inject_val_func = "inject_"
                match node.type_:
                    case PyInt():
                        inject_val_func = "inject_int"
                    case PyBool():
                        inject_val_func = "inject_bool"
                    case _:
                        raise NotImplementedError(
                            "unimplemented list element type: ",
                            node.annotation.slice.id,
                        )
                val_func = Call(
                    func=Name(inject_val_func, Load()),
                    args=[node.value],
                    keywords=[],
                )
            node = Expr(
                value=Call(
                    func=Name("set_subscript", Load()),
                    args=[
                        node.targets[0].value,
                        Call(
                            func=Name("inject_int", Load()),
                            args=[node.targets[0].slice],
                            keywords=[],
                        ),
                        val_func,
                    ],
                    keywords=[],
                )
            )
            return node
        return node

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        self.generic_visit(node)
        if isinstance(node.value, List):
            #print(ast.dump(node))
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
                # for lists and dicts call normally, else need to inject
                val_func = None
                if isinstance(val, List):
                    val_func = val
                else:
                    inject_val_func = "inject_"
                    match node.annotation.slice.id:
                        case "int":
                            inject_val_func = "inject_int"
                        case "bool":
                            inject_val_func = "inject_bool"
                        case _:
                            raise NotImplementedError(
                                "unimplemented list element type: ",
                                node.annotation.slice.id,
                            )
                    val_func = Call(
                        func=Name(inject_val_func, Load()),
                        args=[val],
                        keywords=[],
                    )
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
                                val_func,
                            ],
                            keywords=[],
                        )
                    )
                )
            return new_body
        a = Assign(targets=[node.target], value=node.value)
        a.type_ = node.type_
        return a

    def visit_Call(self, node: Call) -> Any:
        self.generic_visit(node)
        if isinstance(node.func, Name):
            if node.func.id == "print":
                if isinstance(node.type_, PyInt):
                    node.func.id = "print_int_nl"
                elif isinstance(node.type_, PyBool):
                    node.func.id = "print_bool_nl"
                    # node.args[0] = Call(func=Name("inject_bool", ctx=Load()), args=[node.args[0]], keywords=[])
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
                if isinstance(node.types_[0], (PyList, PyDict)) or isinstance(
                    node.types_[1], (PyList, PyDict)
                ):
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
                if isinstance(node.types_[0], (PyList, PyDict)) or isinstance(
                    node.types_[1], (PyList, PyDict)
                ):
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

    def visit_Subscript(self, node):
        self.generic_visit(node)
        # if the subscript is part of a type annotation or its a Store, ignore it
        if (hasattr(node.value, "id") and node.value.id == "list") or isinstance(
            node.ctx, Store
        ):
            return node
        parent = node.parent
        # try to get parent type, assume int by default
        parent_type = PyInt()
        if hasattr(parent, "type_"):
            parent_type = parent.type_
        node = Call(
            func=Name("get_subscript", ctx=Load()),
            args=[
                node.value,
                Call(func=Name("inject_int", Load()), args=[node.slice], keywords=[]),
            ],
            keywords=[],
        )
        if isinstance(parent, Subscript):
            return node
        match parent_type:
            case PyInt():
                node = Call(func=Name("project_int", Load()), args=[node], keywords=[])
            case PyBool():
                node = Call(func=Name("project_bool", Load()), args=[node], keywords=[])
        return node

    def visit_Constant(self, node):
        if node.value == True:
            node.value = 1
        elif node.value == False:
            node.value = 0
        return node


def dispatch(ast_: AST):
    d = Dispatcher()
    return ast.fix_missing_locations(d.visit(ast_))

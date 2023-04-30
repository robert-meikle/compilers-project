import ast
import logging
import os
import sys
import copy
from _ast import BinOp
from ast import *

from pytypes import *

types = {"int", "bool", "list", "dict", "None"}


class TypeErrorReporter:
    program: str

    @staticmethod
    def report(e: str, lineno: int, col: int):
        line = TypeErrorReporter.program.splitlines()[lineno - 1]
        logging.error("\n%s", e)
        logging.error("\t%s", line)
        logging.error("\t%s^", " " * col)
        exit(-1)


class TypeChecker:
    def __init__(self) -> None:
        self.tenv: dict[str, PyType] = {
            "print": PyFunc([PyAny()], PyVoid()),
            "int": PyFunc([PyAny()], PyInt()),
        }
        self.current_func = ""
        self.func_signatures: dict[str, list[PyType]] = {}

    def name_to_pytype(self, name_: str) -> PyType:
        if name_ == "int":
            return PyInt()
        if name_ == "bool":
            return PyBool()
        if name_ == "dict":
            return PyDict(PyVoid(), PyVoid())
        if name_ == "list":
            return PyList(PyVoid())
        return PyVoid()

    def eval_annot_type(self, annot) -> PyType:
        if isinstance(annot, Name):
            return self.name_to_pytype(annot.id)
        if isinstance(annot, Subscript):
            assert isinstance(annot.value, Name)
            if annot.value.id == "list":
                return PyList(self.eval_annot_type(annot.slice))
            elif annot.value.id == "dict":
                assert isinstance(annot.slice, Tuple)
                key_val_types = annot.slice.elts
                return PyDict(
                    self.eval_annot_type(key_val_types[0]),
                    self.eval_annot_type(key_val_types[1]),
                )
            else:
                raise NotImplementedError(
                    f"Unexpected name in type annotation, '{type(annot.value.id)}'"
                )

        return PyVoid()

    def eval_function_def(self, node) -> PyType:
        assert isinstance(node, FunctionDef)
        ret_type = self.eval_annot_type(node.returns)
        arg_types = []
        for arg_obj in node.args.args:
            arg_t = self.eval_annot_type(arg_obj.annotation)
            self.tenv[arg_obj.arg] = arg_t
            arg_types.append(arg_t)

        return PyFunc(arg_types, ret_type)

    def type_check(self, node: AST) -> PyType:
        match node:
            case Module():
                result_type = PyVoid()
                for statement in node.body:
                    result_type = self.type_check(statement)
                logging.info("No type errors found.")
                return result_type
            case Assign():
                expr_type = self.type_check(node.value)

                if isinstance(node.targets[0], Name):
                    if isinstance(expr_type, PyFunc):
                        self.tenv[node.targets[0].id] = expr_type
                        return PyVoid()
                    elif node.targets[0].id not in self.tenv:
                        TypeErrorReporter.report(
                            f"[Line {node.lineno}:{node.col_offset}] Assignment requires type annotation.",
                            node.lineno,
                            node.col_offset,
                        )

                match node.targets[0]:
                    case Subscript():
                        expected_t = self.type_check(node.targets[0].value)
                    case Name():
                        expected_t = self.type_check(node.targets[0])
                    case _:
                        raise NotImplementedError(
                            f"Unexpected situation in Assign, '{type(node.targets[0])}'"
                        )

                if expr_type != expected_t:
                    TypeErrorReporter.report(
                        f'[Line {node.lineno}:{node.col_offset}] Incompatible types in assignment (expression has type "{expr_type}", variable has type "{expected_t}")',
                        node.lineno,
                        node.col_offset,
                    )
                return PyVoid()

            case AnnAssign():
                expected = self.eval_annot_type(node.annotation)
                expr_type = self.type_check(node.value)

                if expr_type != expected:
                    TypeErrorReporter.report(
                        f'[Line {node.lineno}:{node.col_offset}] Incompatible types in assignment (expression has type "{expr_type}", variable has type "{expected}")',
                        node.lineno,
                        node.col_offset,
                    )

                if isinstance(node.target, Name):
                    self.tenv[node.target.id] = expected
                else:
                    raise NotImplementedError(
                        f"AnnAssign target not Name '{type(node.target)}'"
                    )
                return PyVoid()

            case BinOp():
                left_t = self.type_check(node.left)
                right_t = self.type_check(node.right)

                assert isinstance(node.op, Add)

                if isinstance(left_t, (PyInt, PyBool)) and isinstance(
                    right_t, (PyInt, PyBool)
                ):
                    return PyInt()

                if left_t == right_t and isinstance(left_t, PyList):
                    return left_t

                TypeErrorReporter.report(
                    f'[Line {node.lineno}:{node.col_offset}] Unsupported operand types for "+" ("{left_t}", "{right_t}")',
                    node.lineno,
                    node.col_offset,
                )
            case UnaryOp():
                operand_t = self.type_check(node.operand)

                match node.op:
                    case USub():
                        if isinstance(operand_t, (PyInt, PyBool)):
                            return PyInt()
                        TypeErrorReporter.report(
                            f'[Line {node.lineno}:{node.col_offset}] Unsupported operand type for unary "{type(node.op)}" ("{operand_t}")',
                            node.lineno,
                            node.col_offset,
                        )
                    case Not():
                        return PyBool()
                    case _:
                        raise NotImplementedError(
                            f"Unimplemented UnaryOp '{type(node.op)}'"
                        )

            case Compare():
                _ = self.type_check(node.left)
                for c in node.comparators:
                    _ = self.type_check(c)

                return PyBool()
            case BoolOp():
                if len(node.values) > 0:
                    t_0 = self.type_check(node.values[0])

                    for val in node.values[1:]:
                        t_i = self.type_check(val)
                        if t_i != t_0:
                            TypeErrorReporter.report(
                                f'[Line {val.lineno}:{val.col_offset}] BoolOp contains non-uniform types ("{t_0}", "{t_i}")',
                                val.lineno,
                                val.col_offset,
                            )
                    return t_0
                return PyVoid()
            case Call():
                arg_types = []
                for arg_ in node.args:
                    arg_types.append(self.type_check(arg_))

                result_type = self.type_check(node.func)

                if not isinstance(result_type, PyFunc):
                    TypeErrorReporter.report(
                        f'[Line {node.lineno}:{node.col_offset}] "{result_type}" not callable.',
                        node.lineno,
                        node.col_offset,
                    )

                for i, arg_t in enumerate(zip(arg_types, result_type.arg_types)):
                    if arg_t[0] != arg_t[1]:
                        TypeErrorReporter.report(
                            f'[Line {node.lineno}:{node.col_offset}] Argument {i + 1} has incompatible type, got "{arg_t[0]}" expected "{arg_t[1]}".',
                            node.args[i].lineno,
                            node.args[i].col_offset,
                        )

                return result_type.return_type

            case IfExp():
                true_t = self.type_check(node.body)
                false_t = self.type_check(node.orelse)

                if true_t != false_t:
                    TypeErrorReporter.report(
                        f'[Line {node.lineno}:{node.col_offset}] Conditional evaluates to multiple types ("{true_t}", "{false_t}")',
                        node.lineno,
                        node.col_offset,
                    )
                return true_t
            case FunctionDef():
                outer_tenv = copy.deepcopy(self.tenv)

                expected_t = self.eval_annot_type(node.returns)
                arg_types = []
                for arg_obj in node.args.args:
                    arg_t = self.eval_annot_type(arg_obj.annotation)
                    self.tenv[arg_obj.arg] = arg_t
                    arg_types.append(arg_t)

                actual_t = PyVoid()
                for statement in node.body:
                    actual_t = self.type_check(statement)

                self.tenv = outer_tenv
                if actual_t != expected_t:
                    TypeErrorReporter.report(
                        f'[Line {node.lineno}:{node.col_offset}] Incompatible return value type (got "{actual_t}", expected "{expected_t}")',
                        node.lineno,
                        node.col_offset,
                    )

                self.tenv[node.name] = PyFunc(arg_types, expected_t)

                return PyVoid()
            case Return():
                return self.type_check(node.value)

            case If():
                _ = self.type_check(node.test)
                for statement in node.body:
                    _ = self.type_check(statement)
                for statement in node.orelse:
                    _ = self.type_check(statement)
                return PyVoid()

            case While():
                _ = self.type_check(node.test)
                for statement in node.body:
                    _ = self.type_check(statement)
                for statement in node.orelse:
                    _ = self.type_check(statement)
                return PyVoid()

            case Subscript():
                obj_t = self.type_check(node.value)

                match obj_t:
                    case PyList():
                        return obj_t.content_type
                    case _:
                        raise NotImplementedError("only list subscript")
            case Expr():
                return self.type_check(node.value)
            case Constant():
                match node.value:
                    case bool():
                        return PyBool()
                    case int():
                        return PyInt()
                    case _:
                        raise RuntimeError("Constant failed to evaluate to int or bool")
            case List():
                if len(node.elts) > 0:
                    t_0 = self.type_check(node.elts[0])

                    for elt in node.elts[1:]:
                        t_i = self.type_check(elt)
                        if t_i != t_0:
                            TypeErrorReporter.report(
                                f'[Line {elt.lineno}:{elt.col_offset}] List contains non-uniform types ("{t_0}", "{t_i}")',
                                elt.lineno,
                                elt.col_offset,
                            )
                    return PyList(t_0)
                return PyList(PyVoid())
            case Dict():
                assert len(node.keys) == len(
                    node.values
                ), "mismatched number of keys and values in dict"

                if len(node.keys) > 0:
                    key_type = self.type_check(node.keys[0])
                    val_type = self.type_check(node.values[0])

                    for key in node.keys[1:]:
                        key_i = self.type_check(key)
                        if key_i != key_type:
                            TypeErrorReporter.report(
                                f'[Line {key.lineno}:{key.col_offset}] Dict contains non-uniform types ("{key_type}", "{key_i}")',
                                key.lineno,
                                key.col_offset,
                            )
                    for val in node.values[1:]:
                        val_i = self.type_check(val)
                        if val_i != val_type:
                            TypeErrorReporter.report(
                                f'[Line {val.lineno}:{val.col_offset}] Dict contains non-uniform types ("{val_type}", "{val_i}")',
                                val.lineno,
                                val.col_offset,
                            )
                    return PyDict(key_type, val_type)
                return PyDict(PyVoid(), PyVoid())
            case Name():
                return self.tenv[node.id]
            case _:
                raise NotImplementedError(
                    f"AST node '{type(node)}' not implemented in type checker."
                )


def checker():
    """
    Runs the type checker.
    """
    if not os.path.isfile(sys.argv[1]):
        raise FileNotFoundError(f"'{sys.argv[1]}' does not correspond to a valid file.")

    prog = ""
    with open(sys.argv[1], "r", encoding="utf-8") as file_:
        prog = file_.read()

    TypeErrorReporter.program = prog
    ast_ = ast.parse(prog)

    logging.info(ast.unparse(ast_))

    # logging.info("%s\n", ast.dump(ast_, indent=4))

    # collect global function defs
    type_checker = TypeChecker()
    for node in ast_.body:
        if isinstance(node, FunctionDef):
            type_checker.tenv[node.name] = type_checker.eval_function_def(node)

    _ = type_checker.type_check(ast_)


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    logging.getLogger(__name__)

    if len(sys.argv) < 2:
        raise SyntaxError(f"Improper Usage: {sys.argv} <path to program to parse>.")

    checker()

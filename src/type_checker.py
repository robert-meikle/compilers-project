import ast
import logging
import os
import sys
from _ast import Add, BinOp
from ast import *

from pytypes import *

types = {"int", "bool", "list", "dict", "None"}
builtin_funcs = {"print": PyVoid()}


class NameGen:
    tmp_count = 0
    fmt = "tmp{}"

    @staticmethod
    def just_name():
        name_ = NameGen.fmt.format(NameGen.tmp_count)
        NameGen.tmp_count += 1
        return Name(id=name_, ctx=Store())

    @staticmethod
    def create_name(value: AST, acc: list[AST]):
        tmp_name = NameGen.fmt.format(NameGen.tmp_count)
        NameGen.tmp_count += 1
        tmp = Name(id=tmp_name, ctx=Store())
        acc.append(Assign([tmp], value))
        return Name(id=tmp_name, ctx=Load())


class TypeErrorReporter:
    program: str

    @staticmethod
    def report(e: str, lineno: int, col: int):
        line = TypeErrorReporter.program.splitlines()[lineno - 1]
        logging.error(e)
        logging.error("\t%s", line)
        logging.error("\t%s^", " " * col)
        exit(-1)


class TypeChecker:
    def __init__(self) -> None:
        self.tenv: dict[str, PyType] = {}

    def eval_const_type(self, c: Constant) -> PyType:
        match c.value:
            case int():
                return PyInt()
            case bool():
                return PyBool()
            case _:
                raise RuntimeError("Constant failed to evaluate to int or bool")

    def eval_type(self, node) -> PyType:
        if isinstance(node, Constant):
            return self.eval_const_type(node)

        if isinstance(node, Name):
            return self.tenv[node.id]

        if isinstance(node, List):
            if len(node.elts) > 0:
                t_0 = self.eval_type(node.elts[0])

                for elt in node.elts[1:]:
                    t_i = self.eval_type(elt)
                    if t_i != t_0:
                        TypeErrorReporter.report(
                            f'[Line {elt.lineno}:{elt.col_offset}] List contains non-uniform types ("{t_0}", "{t_i}")',
                            elt.lineno,
                            elt.col_offset,
                        )
                return PyList(t_0)
            return PyList(PyVoid())

        if isinstance(node, Dict):
            assert len(node.keys) == len(
                node.values
            ), "mismatched number of keys and values in dict"

            if len(node.keys) > 0:
                key_type = self.eval_type(node.keys[0])
                val_type = self.eval_type(node.values[0])

                for key in node.keys[1:]:
                    key_i = self.eval_type(key)
                    if key_i != key_type:
                        TypeErrorReporter.report(
                            f'[Line {key.lineno}:{key.col_offset}] Dict contains non-uniform types ("{key_type}", "{key_i}")',
                            key.lineno,
                            key.col_offset,
                        )
                for val in node.values[1:]:
                    val_i = self.eval_type(val)
                    if val_i != val_type:
                        TypeErrorReporter.report(
                            f'[Line {val.lineno}:{val.col_offset}] Dict contains non-uniform types ("{val_type}", "{val_i}")',
                            val.lineno,
                            val.col_offset,
                        )
                return PyDict(key_type, val_type)
            return PyDict(PyVoid(), PyVoid())

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

    def type_check(self, node: AST) -> PyType:
        match node:
            case Module():
                result_type = PyVoid()
                for statement in node.body:
                    result_type = self.type_check(statement)
                logging.info("No type errors found.")
                return result_type
            case Assign():
                if isinstance(node.targets[0], Name):
                    if node.targets[0].id not in self.tenv:
                        TypeErrorReporter.report(
                            f"[Line {node.lineno}:{node.col_offset}] Assignment requires type annotation.",
                            node.lineno,
                            node.col_offset,
                        )

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

                if isinstance(left_t, (PyInt, PyBool)) and isinstance(
                    right_t, (PyInt, PyBool)
                ):
                    return PyInt()

                if left_t != right_t:
                    TypeErrorReporter.report(
                        f'[Line {node.lineno}:{node.col_offset}] Unsupported operand types for "{type(node.op)}" ("{left_t}", "{right_t}")',
                        node.lineno,
                        node.col_offset,
                    )

                return left_t
            case UnaryOp():
                operand_t = self.type_check(node.operand)

                if isinstance(operand_t, (PyInt, PyBool)):
                    return PyInt()
                TypeErrorReporter.report(
                    f'[Line {node.lineno}:{node.col_offset}] Unsupported operand type for unary "{type(node.op)}" ("{operand_t}")',
                    node.lineno,
                    node.col_offset,
                )

            case Call():
                arg_types = []
                for arg_ in node.args:
                    arg_types.append(self.type_check(arg_))

                if isinstance(node.func, Name):
                    if node.func.id in builtin_funcs:
                        return builtin_funcs[node.func.id]
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
            case Expr():
                return self.type_check(node.value)
            case List() | Dict() | Constant():
                return self.eval_type(node)
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

    logging.info("%s\n", ast.unparse(ast_))

    # logging.info("%s\n", ast.dump(ast_, indent=4))

    type_checker = TypeChecker()
    _ = type_checker.type_check(ast_)


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    logging.getLogger(__name__)

    if len(sys.argv) < 2:
        raise SyntaxError(f"Improper Usage: {sys.argv} <path to program to parse>.")

    checker()

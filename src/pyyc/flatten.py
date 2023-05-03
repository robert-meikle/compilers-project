import ast
import copy
from ast import *


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


def flatten(node: AST, acc: list[AST]) -> AST:
    match node:
        case Constant() | Name():
            return node
        case List():
            node.elts = [flatten(e, acc) for e in node.elts]
            match node.parent:
                case Assign():
                    return node
                case _:
                    return NameGen.create_name(node, acc)
        case Dict():
            node.keys = [flatten(e, acc) for e in node.keys]
            node.values = [flatten(e, acc) for e in node.values]
            match node.parent:
                case Assign():
                    return node
                case _:
                    return NameGen.create_name(node, acc)
        case Subscript():
            return node
        case Module():
            for e in node.body:
                acc.append(flatten(e, acc))
            return ast.fix_missing_locations(Module(acc, []))
        case Assign() | Expr():
            if isinstance(node.value, IfExp):
                test_inst = []
                test = flatten(node.value.test, test_inst)

                if_inst = []
                if_ = flatten(node.value.body, if_inst)

                node.value = flatten(node.value.orelse, acc)

                acc.append(node)
                acc += test_inst

                return If(test, if_inst + [Assign([node.targets[0]], if_)], [])
            elif isinstance(node.value, BoolOp):
                left = flatten(node.value.values[0], acc)

                right_instrs = []
                right = flatten(node.value.values[1], right_instrs)

                if isinstance(node.value.op, And):
                    new_if = If(
                        test=left,
                        body=right_instrs + [Assign(node.targets, right)],
                        orelse=[],
                    )

                    acc += [Assign(node.targets, left)]
                    return new_if
                elif isinstance(node.value.op, Or):
                    new_if = If(
                        test=UnaryOp(op=Not(), operand=left),
                        body=right_instrs + [Assign(node.targets, right)],
                        orelse=[],
                    )

                    acc += [Assign(node.targets, left)]
                    return new_if
                else:
                    raise RuntimeError(f"Unknown op in BoolOp: '{type(node.value.op)}'")
            else:
                node.value = flatten(node.value, acc)
                return node
        case BinOp():
            node.left = flatten(node.left, acc)
            node.right = flatten(node.right, acc)
            match node.parent:
                case Assign():
                    return node
                case _:
                    return NameGen.create_name(node, acc)
        case UnaryOp():
            node.operand = flatten(node.operand, acc)
            node.operand = (
                NameGen.create_name(node.operand, acc)
                if isinstance(node.operand, Constant)
                else node.operand
            )
            match node.parent:
                case Assign():
                    return node
                case _:
                    return NameGen.create_name(node, acc)
        case Call():
            if isinstance(node.func, Name) and node.func.id == "input":
                return node
            node.args = [flatten(a, acc) for a in node.args]
            node.func = flatten(node.func, acc)
            match node.parent:
                case Assign() | Expr():
                    return node
                case _:
                    return NameGen.create_name(node, acc)
        case BoolOp():
            # case where parent is an assign is handled in Assign section
            assign_target = NameGen.just_name()

            left = flatten(node.values[0], acc)

            right_instrs = []
            right = flatten(node.values[1], right_instrs)

            if isinstance(node.op, And):
                new_if = If(
                    test=left,
                    body=right_instrs + [Assign([assign_target], right)],
                    orelse=[],
                )

                acc += [Assign([assign_target], left), new_if]
            elif isinstance(node.op, Or):
                new_if = If(
                    test=UnaryOp(op=Not(), operand=left),
                    body=right_instrs + [Assign([assign_target], right)],
                    orelse=[],
                )

                acc += [Assign([assign_target], left), new_if]
            else:
                raise RuntimeError(f"Unknown op in BoolOp: '{type(node.op)}'")

            return Name(assign_target.id, ctx=Load())
        case Compare():
            node.left, node.comparators = flatten(node.left, acc), [
                flatten(c, acc) for c in node.comparators
            ]
            node.left = (
                NameGen.create_name(node.left, acc)
                if isinstance(node.left, Constant)
                else node.left
            )
            for i, comp in enumerate(node.comparators):
                node.comparators[i] = (
                    NameGen.create_name(comp, acc)
                    if isinstance(comp, Constant)
                    else comp
                )
            match node.parent:
                case Assign():
                    return node
                case _:
                    return NameGen.create_name(node, acc)
        case If():
            node.test = flatten(node.test, acc)
            node.test = (
                NameGen.create_name(node.test, acc)
                if isinstance(node.test, Constant)
                else node.test
            )
            body_ = []
            for elt in node.body:
                body_.append(flatten(elt, body_))

            _else = []
            for elt in node.orelse:
                _else.append(flatten(elt, _else))
            node.body, node.orelse = body_, _else
            return node
        case While():
            _test = []
            node.test = flatten(node.test, _test)
            node.test = (
                NameGen.create_name(node.test, acc)
                if isinstance(node.test, Constant)
                else node.test
            )
            acc += _test
            body_ = []
            for elt in node.body:
                body_.append(flatten(elt, body_))
            node.body = body_ + copy.deepcopy(_test)
            return node
        case IfExp():
            assign_target = NameGen.just_name()

            test = flatten(node.test, acc)

            if_ = flatten(node.body, acc)

            acc += [Assign([assign_target], if_)]

            else_inst = []
            else_ = flatten(node.orelse, else_inst)

            new_if = If(
                test=UnaryOp(op=Not(), operand=test),
                body=else_inst + [Assign([assign_target], else_)],
                orelse=[],
            )
            acc += [new_if]
            return Name(assign_target.id, ctx=Load())
        case Return():
            node.value = flatten(node.value, acc)
            return node
        case Lambda():
            body_ = []
            for elt in node.body:
                body_.append(flatten(elt, body_))
            node.body = body_
            match node.parent:
                case Assign():
                    return node
                case _:
                    return NameGen.create_name(node, acc)
        case FunctionDef():
            body_ = []
            for elt in node.body:
                body_.append(flatten(elt, body_))
            node.body = body_
            return node
        case _:
            raise NotImplementedError(
                f"Unimplemented node type in flatten, '{type(node)}'"
            )

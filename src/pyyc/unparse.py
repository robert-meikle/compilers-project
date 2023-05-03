import logging
import ast
from ast import *

def unparse(node: AST, depth = 0):
	indent = "\t" * depth
	
	match node:
		case Module():
			return f"\n{indent}".join([str(unparse(x, depth)) for x in node.body]) + "\n"
		case Expr():
			return str(unparse(node.value, depth))
		case Assign():
			return f"{unparse(node.targets[0], depth)} = {unparse(node.value, depth)}"
		case Name():
			return str(node.id)
		case Constant():
			return str(node.value)
		case BinOp():
			return f"{unparse(node.left, depth)} {unparse(node.op, depth)} {unparse(node.right, depth)}"
		case UnaryOp():
			return f"{unparse(node.op, depth)}{unparse(node.operand, depth)}"
		case Call():
			return f"{unparse(node.func, depth)}({', '.join([unparse(a, depth) for a in node.args])})"
		case Lambda():
			args = ""
			for i,x in enumerate(node.args.args): args += x.arg + ("," if i+1 != len(node.args.args) else "")
			_body = f"\n\t{indent}".join([str(unparse(x, depth + 1)) for x in node.body])
			return f"lambda {args}:\n\t{indent}{_body}"
		case FunctionDef():
			args = ""
			for i,x in enumerate(node.args.args): args += x.arg + ("," if i+1 != len(node.args.args) else "")
			_body = f"\n\t{indent}".join([str(unparse(x, depth + 1)) for x in node.body])
			return f"def {node.name}({args}):\n\t{indent}{_body}"
		case BoolOp():
			return f"({f' {unparse(node.op, depth)} '.join([unparse(v, depth) for v in node.values])})"
		case Compare():
			return f"({unparse(node.left, depth)} {' '.join([f'{str(unparse(node.ops[i], depth))} {str(unparse(node.comparators[i], depth))}' for i in range(len(node.ops))])})"
		case List():
			return f"[{','.join([f'{str(unparse(e, depth))}' for e in node.elts])}]"
		case Subscript():
			return f"{str(unparse(node.value, depth))}[{str(unparse(node.slice, depth))}]"
		case Dict():
			return f"{{{','.join([f'{str(unparse(node.keys[i], depth))}: {str(unparse(node.values[i], depth))}' for i in range(len(node.values))])}}}"
		case If():
			_body = f"\n\t{indent}".join([str(unparse(x, depth + 1)) for x in node.body])

			if node.orelse:
				_else = f"\n\t{indent}".join([str(unparse(x, depth + 1)) for x in node.orelse])
				return f"if ({unparse(node.test, depth)}):\n\t{indent}{_body}\n{indent}else:\n\t{indent}{_else}"
			else:
				return f"if ({unparse(node.test, depth)}):\n\t{indent}{_body}"
		case While():
			_body = f"\n\t{indent}".join([str(unparse(x, depth + 1)) for x in node.body])
			return f"while ({unparse(node.test, depth)}):\n\t{indent}{_body}\n"
		case IfExp():
			return f"{unparse(node.body, depth)} if {unparse(node.test, depth)} else {unparse(node.orelse, depth)}"
		case And():
			return "and"
		case Or():
			return "or"
		case Eq():
			return "=="
		case NotEq():
			return "!="
		case Add():
			return "+"
		case USub():
			return "-"
		case Not():
			return "not "
		case Is():
			return "is"
		case Return():
			return f"return {unparse(node.value, depth)}"
		case _:
			raise NotImplementedError(f"Unimplemented node type in unparse, '{type(node)}'")
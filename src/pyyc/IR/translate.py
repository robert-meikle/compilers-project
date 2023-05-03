from ast import *
from IR.ir import *

"""
project_int(x)
shr 2, x

inject_int(x)
shl 2,x
orl 3,x

"""
def node_to_ir(node: AST):
	match node:
		case Name():
			return IR_Var(node.id)
		case Constant():
			return IR_Const(node.value)
		case Expr():
			return node_to_ir(node.value)
		case Call():
			if isinstance(node.func, Name) and node.func.id == "eval":
				return IR_Call(IR_Var("eval_input_pyobj"), [])
			else:
				return IR_Call(node_to_ir(node.func), [node_to_ir(a) for a in node.args], None)
		case Return():
			return IR_Return(node_to_ir(node.value))
		case Assign():
			dst = node_to_ir(node.targets[0])

			match node.value:
				case Call():
					c: IR_Call = node_to_ir(node.value)
					c.dst = dst
					return IR_Call(IR_Var(c.func_name), c.args, dst)
				case BinOp():
					left, right = node_to_ir(node.value.left), node_to_ir(node.value.right)
					op = node_to_ir(node.value.op)
					if left == dst:
						return IR_Binop(op, right, dst)
					elif right == dst:
						return IR_Binop(op, left, dst)
					else:
						return [IR_Mov(left, dst), IR_Binop(op, right, dst)]
				case UnaryOp():
					op = node_to_ir(node.value.op)
					operand = node_to_ir(node.value.operand)
					if operand == dst:
						return IR_Unop(op, operand)
					else:
						return [IR_Mov(operand, dst), IR_Unop(op, dst)]
				case BoolOp():
					op = node_to_ir(node.value.op)
					s1 = node_to_ir(node.value.values[0])
					s2 = node_to_ir(node.value.values[1])
					return IR_Boolop(op, s1, s2, dst)
				case Compare():
					op = node_to_ir(node.value.ops[0])
					return IR_Compare(op, node_to_ir(node.value.left), node_to_ir(node.value.comparators[0]), dst)
				case _:
					return IR_Mov(node_to_ir(node.value), dst)
		  
		case And():
			return "and"
		case Or():
			return "or"
		case Eq():
			return "equals"
		case NotEq():
			return "nequals"
		case Add():
			return "addl"
		case USub():
			return "negl"
		case Not():
			return "not"
		case Return():
			return node_to_ir(node.value)
		case _:
			raise Exception(f"Unhandled node type in translate, '{node} : {type(node)}'")
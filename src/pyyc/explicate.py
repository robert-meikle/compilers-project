import ast
import logging
import os
import sys
from ast import *
from flatten import flatten
from util import add_parents
from unparse import unparse

# format {c} = {a} + {b}
add_code = """
if (is_int({a})):
	if (is_big({b})):
		error_pyobj()
	else:
		if (is_int({b})):
			{c} = inject_int(project_int({a})+ project_int({b}))
		else:
			{c} = inject_int(project_int({a})+ project_bool({b}))
elif (is_big({a})):
	if is_big({b}):
		{c} = inject_big(add(project_big({a}), project_big({b})))
	else: # {b} is bool
		error_pyobj()	
else:
	if (is_big({b})):
		error_pyobj()
	else:
		{c} = inject_int(project_bool({a})+ project_int({b}))"""

# format {c} = -{a}
usub_code = """
if (is_int({a})):
	{c} = inject_int(-project_int({a}))	
else:
	error_pyobj()
"""

# format {c} = {a} == {b}
equals_code = """
if (is_int({a})):
	if (is_int({b})):
		{c} = inject_bool(project_int({a}) == project_int({b}))
	elif is_big({b}):
		{c} = inject_bool(0)
	else: # {b} is bool
		{c} = inject_bool(project_int({a}) == project_bool({b}))
		
elif (is_big({a})):
	if (is_int({b})):
		{c} = inject_bool(0)
	elif is_big({b}):
		{c} = inject_bool(equal(project_big({a}), project_big({b})))
	else: # {b} is bool
		{c} = inject_bool(0)
		
else:
	if (is_int({b})):
		{c} = inject_bool(project_bool({a}) == project_int({b}))
	elif is_big({b}):
		{c} = inject_bool(0)
	else: # {b} is bool
		{c} = inject_bool(project_bool({a}) == project_bool({b}))"""

# format {c} = {a} != {b}
notequals_code = """
if (is_int({a})):
	if (is_int({b})):
		{c} = inject_bool(project_int({a}) != project_int({b}))
	elif is_big({b}):
		{c} = inject_bool(0)
	else: # {b} is bool
		{c} = inject_bool(project_int({a}) != project_bool({b}))		
elif (is_big({a})):
	if (is_int({b})):
		{c} = inject_bool(0)
	elif is_big({b}):
		{c} = inject_bool(not_equal(project_big({a}), project_big({b})))
	else: # {b} is bool
		{c} = inject_bool(0)	
else:
	if (is_int({b})):
		{c} = inject_bool(project_bool({a}) != project_int({b}))
	elif is_big({b}):
		{c} = inject_bool(0)
	else: # {b} is bool
		{c} = inject_bool(project_bool({a}) != project_bool({b}))"""

# format {c} = {a} is {b}
is_code = """
if (is_int({a})):
	if (is_int({b})):
		{c} = inject_bool(project_int({a}) == project_int({b}))
	else:
		{c} = inject_bool(0)
		
elif (is_big({a})):
	if is_big({b}):
		{c} = inject_bool(equal(project_big({a}), project_big({b})))
	else:
		{c} = inject_bool(0)	
else:
	if (is_bool({b})):
		{c} = inject_bool(project_bool({a}) == project_bool({b}))
	else:
		{c} = inject_bool(0)"""

class ConstantExplicator(ast.NodeTransformer):
	def visit_Constant(self, node):
		if type(node.value) is int:
			return Call(func=Name("inject_int", Load()), args=[node], keywords=[])
		elif type(node.value) is bool:
			if node.value:
				return Call(func=Name("inject_bool", Load()), args=[Constant(1)], keywords=[])
			else:
				return Call(func=Name("inject_bool", Load()), args=[Constant(0)], keywords=[])
		else:
			return node
	def visit_Assign(self, node):
		self.generic_visit(node)
		if isinstance(node.targets[0], Subscript):
			return Expr(Call(func=Name("set_subscript", Load()), args=[
				node.targets[0].value,
				node.targets[0].slice,
				node.value
			], keywords=[]))
		else:
			return node
		
	def visit_Subscript(self, node):
		self.generic_visit(node)
		if (isinstance(node.ctx, Store)):
			return node
		return Call(func=Name("get_subscript", Load()), args=[node.value, node.slice], keywords=[])

	def visit_Call(self, node):
		self.generic_visit(node)
		if node.func.id == "int":
			return Call(func=Name("inject_int", Load()), args=[
				Call(func=Name("project_bool", Load()), args=node.args, keywords=[])
			], keywords=[])
		#elif node.func.id[-1].isdigit():
		#	return Call(func = Name("inject_big", ctx = Load()), args = [node], keywords = [])
		else:
			return node
	def visit_If(self, node):
		self.generic_visit(node)
		node.test = Call(func=Name("is_true", Load()), args=[node.test], keywords=[])
		return node
	def visit_While(self, node):
		self.generic_visit(node)
		node.test = Call(func=Name("is_true", Load()), args=[node.test], keywords=[])
		return node
	"""
	def visit_BoolOp(self, node):
		new_values = []
		for val in node.values:
			new_values.append(Call(func=Name("is_true", Load()), args=[val], keywords=[]))
		node.values = new_values
		
		return node
	"""

class NodeExplicator(ast.NodeTransformer):
	def visit_Assign(self, node):
		self.generic_visit(node.value)
		
		if isinstance(node.value, BinOp):
			if isinstance(node.value.op, Add):
				temp = add_code.format(a = node.value.left.id, b = node.value.right.id, c = node.targets[0].id)
				add_tree = ast.parse(temp)
				return add_tree.body
			
		if isinstance(node.value, UnaryOp):
			if isinstance(node.value.op, USub):
				temp = usub_code.format(a = node.value.operand.id, c = node.targets[0].id)
				usub_tree = ast.parse(temp)
				return usub_tree.body
			elif isinstance(node.value.op, Not):
				node.value = Call(func=Name("inject_bool", Load()), args=[
					UnaryOp(op=Not(), operand = Call(func=Name("is_true", Load()), args=[node.value.operand], keywords=[]))
				], keywords=[])
				return node
			
		if isinstance(node.value, Compare):
			if isinstance(node.value.ops[0], Eq):
				temp = equals_code.format(a = node.value.left.id, b = node.value.comparators[0].id, c = node.targets[0].id)
				equals_tree = ast.parse(temp)
				return equals_tree.body
			elif isinstance(node.value.ops[0], Is):
				temp = is_code.format(a = node.value.left.id, b = node.value.comparators[0].id, c = node.targets[0].id)
				is_tree = ast.parse(temp)
				return is_tree.body
			elif isinstance(node.value.ops[0], NotEq):
				temp = notequals_code.format(a = node.value.left.id, b = node.value.comparators[0].id, c = node.targets[0].id)
				not_equals_tree = ast.parse(temp)
				return not_equals_tree.body
			
		if isinstance(node.value, List):
			# assign to create_list
			new_body = [Assign(targets=node.targets, value = 
				Call(func=Name("inject_big", Load()), args=[
					Call(func=Name("create_list", Load()), args=[
						Call(func=Name("inject_int", Load()), args=[Constant(len(node.value.elts))], keywords=[])
					], keywords=[])
				], keywords=[])
			)]
			# populate list
			for i,val in enumerate(node.value.elts):
				new_body.append(
					Expr(value = 
						Call(func=Name("set_subscript", Load()), args=[
							node.targets[0],
							Call(func=Name("inject_int", Load()),args=[Constant(i)], keywords=[]),
							val
						], keywords=[])
					)
				)
			return new_body
		
		if isinstance(node.value, Dict):
			keys = node.value.keys
			values = node.value.values
			
			assert len(keys) == len(values)
			
			# assign to create_dict
			new_body = [Assign(targets=node.targets, value = 
				Call(func=Name("inject_big", Load()), args=[
					Call(func=Name("create_dict", Load()), args=[], keywords=[])
				], keywords=[])
			)]
			# populate dict
			for key,val in zip(keys,values):
				new_body.append(
					Expr(value = 
						Call(func=Name("set_subscript", Load()), args=[node.targets[0], key, val], keywords=[])
					)
				)
			return new_body
		return node
		
def explicate(_ast):
	first_pass = ConstantExplicator()
	_ast = ast.fix_missing_locations(first_pass.visit(_ast))
	_ast = add_parents(_ast)
	
	flatpy = unparse(_ast)
	logging.info(f"\nFirst Pass - Inject Constant Assignments\n-----------------\n{flatpy}")
	logging.info(ast.dump(_ast, indent=2))
	logging.info("*****")
	_ast = flatten(_ast, [])
	logging.info(ast.dump(_ast, indent=2))
	
	
	
	transformer = NodeExplicator()
	_ast = transformer.visit(_ast)
	_ast = add_parents(_ast)
	_ast = flatten(_ast, [])
	flatpy = unparse(_ast)
	logging.info(f"\nSecond Pass\n-----------------\n{flatpy}")
	logging.info(ast.dump(_ast, indent=2))

	return _ast
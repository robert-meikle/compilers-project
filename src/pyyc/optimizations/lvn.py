import copy

from IR.ir import *
from liveness import *
from cfg import CFGNode

# generate hash key given instruction and current value numbers
def hash_key(instruction, values):
	# if mov no op to hash
	if (isinstance(instruction, IR_Mov)):
		return f"{instruction.src}"
	# if an IR_Call and is an eval_input_int(), hash must be unique
	if (isinstance(instruction, IR_Call)):
		if (instruction.func_name == "eval_input_int"):
			return f"{instruction.func_name}_{instruction.id}"
		
	# if has values return hash:
	elif len(instruction.get_values()) > 0:
		hash_str = f"{instruction.op}"
		# append relevant values
		for v in instruction.get_values():
			hash_str += f"_{values[str(v)]}"
		# for binops add dst to hash as well ______ NOTE MIGHT NEED TO FOR BOOLOPS AND COMPARES
		if (isinstance(instruction,IR_Binop)):
			if (str(instruction.dst) in values): # need to cover the case that dst hasent been initialized in the given block
				hash_str += f"_{values[str(instruction.dst)]}"
		return hash_str


# takes a list a block of IR instructions
# returns a list of dictionaries where index i represents the value numbering at instruction i
def lvn(block: CFGNode):
	instructions = block.instructions
	# values is a dictionary assigning values to variables
	values = {}
	
	step_values = [] # holds the value number numbers relating to each instruction
	value_number = 1
	# traverse instructions
	for instruction in instructions:
		# get value numbers for L_i R_i
		for v in instruction.get_values():
			if str(v) not in values:
				values[f"{v}"] = value_number
				value_number += 1
		# there is a case 
		# if the hash_key returns None, no new value numbers need to be created so continue
		if (not hash_key(instruction, values)):
			step_values.append(copy.deepcopy(values))
			continue
		#  if the hash key is already present in the table then associate the value number with dst
		if (hash_key(instruction, values) in values):
			values[f"{instruction.dst}"] = values[hash_key(instruction, values)]
		# else insert a new value number into the table at the hash key location record that new value number for T_i
		else:
			values[hash_key(instruction, values)] = value_number # value number for expression
			values[f"{instruction.dst}"] = value_number # value number for destination
			value_number += 1
			#print(str(instruction),values[f"{instruction.dst}"])
		# deep copy of current values stores as step
		step_values.append(copy.deepcopy(values))
	return step_values

# given an instruction that performs an op on constant(s)
def eval_constant_op(op, v1: int, v2: int):
	match op:
		case "addl":
			return v1 + v2
		case "equals":
			return int(v1 == v2)
		case "nequals":
			return int(v1 != v2)
		case "negl":
			return -v1
		case "not":
			return int(not v1)
		case _:
			raise Exception(f"Unhandled op case: {op}")

def constant_folding(block: CFGNode, step_values):
	print(step_values)
	instructions = block.instructions
	# if the dst for an instruction comes from operands marked as "constant" mark it as constant
	value_to_constant = {} # maps value numbers to constant values
	
	# iterate through instructions and mark constants
	for i,instruction in enumerate(instructions):
		# check for an actual constant in src values
		for v in instruction.get_values():
			if isinstance(v,IR_Const):
				value_to_constant[step_values[i][str(v)]] = v.value
		#print(value_to_constant)
		vals = instruction.get_values()
		# detect if all operands are constant if so Binops, Unops, Compares can be converted to a Mov, and Movs can be removed?
		match instruction:
			case IR_Mov():
				if step_values[i][str(vals[0])] in value_to_constant and isinstance(instruction.src, IR_Const):
					value_to_constant[step_values[i][str(instruction.dst)]] = instruction.src.value # set dst to constant
			case IR_Binop():
				# check that src operands are constant
				srcs_constant = all([step_values[i][str(v)] in value_to_constant for v in vals])
				# check if dst was previosly constant
				if i > 0: # if its the first instruction and is a binop, the dst cant be a constant
					dst_inblock  = str(instruction.dst) in step_values[i-1] # check if initialized in block
					dst_constant = dst_inblock and step_values[i-1][str(instruction.dst)] in value_to_constant
				else:
					dst_constant = False

				if srcs_constant and dst_constant:
					new_val = eval_constant_op(instruction.op, value_to_constant[step_values[i][str(vals[0])]], value_to_constant[step_values[i-1][str(instruction.dst)]])
					# replace instruction with a move
					instructions[i] = IR_Mov(IR_Const(new_val),IR_Var(str(instruction.dst)))
					print(f"changed instruction {i} from {instruction} to {instructions[i]}")
			case IR_Unop():
				# check if dst was already constant
				# check if dst was previosly constant
				if i > 0: # if its the first instruction and is a binop, the dst cant be a constant
					dst_inblock  = str(instruction.dst) in step_values[i-1] # check if initialized in block
					dst_constant = dst_inblock and step_values[i-1][str(instruction.dst)] in value_to_constant
				else:
					dst_constant = False
					
				if dst_constant:
					new_val = eval_constant_op(instruction.op, value_to_constant[step_values[i-1][str(instruction.dst)]],0)
					instructions[i] = IR_Mov(IR_Const(new_val),IR_Var(str(instruction.dst)))
					print(f"changed instruction {i} from {instruction} to {instructions[i]}")
	block.instructions = instructions
	return block

def copy_folding(block: CFGNode, step_values):
	instructions = block.instructions
	# iterate through instructions and mark constants
	for i,instruction in enumerate(instructions):
		if isinstance(instruction, IR_Jmp):
			continue
		# get value_number of dst and check to see if a variable has the same value number
		key = hash_key(instruction,step_values[i])
		key = str(instruction.dst)
		# iterate through value number keys to find a match
		for k in step_values[i].keys():
			if isinstance(instruction, IR_Binop):
				# if a different non constant with the same value number is found check if its live and replace the operation with a move
				if step_values[i][k] == step_values[i][key] and k != key and str(k)[0] != '$':
					if k in block.live_before[i]:
						instructions[i] = IR_Mov(IR_Var(k),IR_Var(str(instruction.dst)))
						print(f"changed instruction {i} from {instruction} to {instructions[i]}")
	block.instructions = instructions
	return block

"""
ins_1 = [IR_Mov(IR_Const(3),IR_Var("x")),IR_Binop("addl",IR_Const(5),IR_Var("x"))]
ins_2 = [IR_Mov(IR_Const(3),IR_Var("x")),IR_Binop("addl",IR_Const(5),IR_Var("x")),IR_Mov(IR_Const(3),IR_Var("y")),IR_Binop("addl",IR_Const(5),IR_Var("y"))]
ins_2 = [IR_Mov(IR_Const(3),IR_Var("x")),IR_Binop("addl",IR_Const(5),IR_Var("x")),IR_Mov(IR_Var("b"),IR_Var("y")),IR_Binop("addl",IR_Const(5),IR_Var("y"))]
ins_2 = [IR_Mov(IR_Const(3),IR_Var("x")),IR_Unop("negl",IR_Var("x")),IR_Mov(IR_Const(3),IR_Var("y")),IR_Binop("addl",IR_Const(5),IR_Var("y"))]

print("lvn: ",lvn(ins_2))
print("constant folding example")
for i in ins_2: print(str(i))
print("to")
ins = constant_folding(ins_2,lvn(ins_2))
for i in ins: print(str(i))

print("copy folding example")
ins = [IR_Mov(IR_Var("_a"),IR_Var("_x")),IR_Binop("addl",IR_Var("_b"),IR_Var("_x")),IR_Mov(IR_Var("_a"),IR_Var("_y")),IR_Binop("addl",IR_Var("_b"),IR_Var("_y")), IR_Mov(IR_Var("_x"),IR_Var("_z"))]
for i in ins: print(str(i))
ins = copy_folding(ins,lvn(ins), block_liveness_analysis(ins))
print("to")
for i in ins: print(str(i))

#[{'$3': 1, 'x': 1}, {'$3': 1, 'x': 3, '$5': 2, 'addl_2_1': 3}, {'$3': 1, 'x': 3, '$5': 2, 'addl_2_1': 3, 'y': 1}, {'$3': 1, 'x': 3, '$5': 2, 'addl_2_1': 3, 'y': 3}]
#[{'$3': 1, 'x': 1}, {'$3': 1, 'x': 3, '$5': 2, 'addl_2': 3}, {'$3': 1, 'x': 3, '$5': 2, 'addl_2': 3, 'y': 1}, {'$3': 1, 'x': 3, '$5': 2, 'addl_2': 3, 'y': 3}]
"""
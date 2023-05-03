import logging

from IR.ir import *

from cfg import CFG


def do_spill_code(cfg: CFG, assignments):
	"""
	Creates spill code, returns a new list of instructions.  Returns new list of
	instructions, the list of unspillables, and a bool corresponding to if more
	rounds are needed.
	"""
	logging.getLogger(__name__)

	allocation_complete = True
	tmp_count = 0

	regs = ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]
	spilled_vars = [a for a in assignments if assignments[a] not in regs]

	logging.info(f"Spilled Variables:\n{spilled_vars}\n")

	unspillables = set()

	for node in cfg.nodes:
		new_instructions = []
		for inst in node.instructions:
			if isinstance(inst, IR_Mov):
				if str(inst.src) in spilled_vars and str(inst.dst) in spilled_vars:
					tmp_var, tmp_count = IR_Var(f"t{tmp_count}"), tmp_count + 1
					new_instructions.append(IR_Mov(inst.src, tmp_var))
					new_instructions.append(IR_Mov(tmp_var, inst.dst))
					
					unspillables.add(str(tmp_var))
				else:
					new_instructions.append(inst)

			elif isinstance(inst, IR_Binop):
				if str(inst.src) in spilled_vars and str(inst.dst) in spilled_vars:
					tmp_var = IR_Var(f"t{tmp_count}")
					new_instructions.append(IR_Mov(inst.src, tmp_var))
					new_instructions.append(IR_Binop(inst.op, tmp_var, inst.dst))
					tmp_count += 1
					unspillables.add(str(tmp_var))
				else:
					new_instructions.append(inst)

			elif isinstance(inst, IR_Compare):
				if inst.dst:
					if str(inst.src1) in spilled_vars and str(inst.src2) in spilled_vars:
						tmp_var = IR_Var(f"t{tmp_count}")
						new_instructions.append(IR_Mov(inst.src1, tmp_var))
						new_instructions.append(IR_Compare(inst.op, tmp_var, inst.src2, inst.dst))
						tmp_count += 1
						unspillables.add(str(tmp_var))
					else:
						new_instructions.append(inst)
				else:
					if str(inst.src1) in spilled_vars and str(inst.src2) in spilled_vars:
						tmp_var = IR_Var(f"t{tmp_count}")
						new_instructions.append(IR_Mov(inst.src1, tmp_var))
						new_instructions.append(IR_Compare(inst.op, tmp_var, inst.src2))
						tmp_count += 1
						unspillables.add(str(tmp_var))
					else:
						new_instructions.append(inst)
			elif isinstance(inst, IR_Boolop):
				if str(inst.src1) in spilled_vars and str(inst.src2) in spilled_vars:
					tmp_var = IR_Var(f"t{tmp_count}")
					new_instructions.append(IR_Mov(inst.src1, tmp_var))
					new_instructions.append(IR_Compare(inst.op, tmp_var, inst.src2))
					tmp_count += 1
					unspillables.add(str(tmp_var))
				else:
					new_instructions.append(inst)
			elif isinstance(inst, IR_Call):
				new_args = []
				for arg in inst.args:
					if str(arg) in spilled_vars:
						tmp_var = IR_Var(f"t{tmp_count}")
						tmp_count += 1
						new_instructions.append(IR_Mov(arg, tmp_var))
						new_args.append(tmp_var)
						unspillables.add(str(tmp_var))
					else:
						new_args.append(arg)
				new_instructions.append(
					IR_Call(IR_Var(inst.func_name), new_args, inst.dst)
				)
			else:
				new_instructions.append(inst)
		node.instructions = new_instructions

	if tmp_count > 0:
		allocation_complete = False

	logging.info(f"Spilled IR\n-----------------")
	for i in new_instructions:
		logging.info(i)

	logging.info(f"Unspillables: {unspillables}")

	if allocation_complete:
		return cfg, spilled_vars, allocation_complete
	else:
		return cfg, list(unspillables), allocation_complete

from cfg import CFGNode
from liveness import block_liveness
from IR.ir import *

def dead_store_elim(bb: CFGNode):
	while True:
		bb, changed = repeated_dse(bb)

		if not changed:
			break
	return bb
def repeated_dse(bb: CFGNode) -> tuple[CFGNode, bool]:
	for i in bb.instructions:
		i.update_rw()

	bb.live_before = [set()] * (len(bb.instructions) + 1)
	bb.live_before[-1] = bb.live_out
	bb = block_liveness(bb)
	bb.show_live()
	
	new_instructions: list[IR_Instruction] = []
	changed = False
	
	for i, inst in enumerate(bb.instructions):
		match inst:
			case IR_Jmp() | IR_Call():
				new_instructions.append(inst)
			case _:
				if isinstance(inst, IR_Compare) and not inst.dst:
					new_instructions.append(inst)
					continue
				if str(inst.dst) in bb.live_before[i + 1]:
					new_instructions.append(inst)
				else:
					changed = True
	bb.instructions = new_instructions
	return bb, changed
from IR.ir import IR_Instruction, IR_Jmp
from cfg import CFG, CFGNode
import logging

def liveness_analysis(cfg: CFG):
	logging.getLogger(__name__)
	for node in cfg.nodes:
		node.live_before = [set()] * (len(node.instructions) + 1)
	q: list[CFGNode] = [cfg.exit]
	visited = [cfg.exit]
	
	while q:
		cur_block = q.pop(0)
		live_out = set()
		for succ in cur_block.successors:
			live_out = live_out.union(succ.live_in)
		
		cur_block.live_out = live_out
		cur_block.live_before[-1] = live_out

		old_live_in = cur_block.live_in
		cur_block = block_liveness(cur_block)

		for pred in cur_block.predecessors:
			if pred not in visited:
				visited.append(pred)
				q.append(pred)
			elif old_live_in != cur_block.live_in:
				q.append(pred)

	return cfg
	

def block_liveness(block: CFGNode):
	for k in range(len(block.instructions) - 1, -1, -1):
		if isinstance(block.instructions[k], IR_Jmp):
			block.live_before[k] = block.live_before[k + 1]
		else:
			block.live_before[k] = (
				block.live_before[k + 1] - block.instructions[k].writes
			) | block.instructions[k].reads
	block.live_in = block.live_before[0]
	return block
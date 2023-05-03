from enum import Enum
from collections import deque
from util import RemoveIntCasts
from IR.translate import *
from IR.ir import *
import logging

class NodeKind(Enum):
	ENTRY = 0
	EXIT = 1
	STATEMENT = 2
	BRANCH = 3

class CFGNode():
	instructions: list[IR_Instruction]

	def __init__(self, id: int, kind: NodeKind) -> None:
		self.id = id
		self.kind = kind
		self.predecessors: list[CFGNode] = []
		self.successors: list[CFGNode] = []
		self.instructions = []

		self.label = f"{self.kind.name}_{str(id)}"

		self.live_in = set()
		self.live_out = set()
		self.live_before = set()

		self.internal_ids = 0

	def append(self, i: list[IR_Instruction] | IR_Instruction):
		if isinstance(i, list):
			for _i in i:
				_i.id = self.internal_ids
				_i.node_id = self.id
				self.internal_ids += 1
			self.instructions += i
		else:
			i.id = self.internal_ids
			i.node_id = self.id
			self.internal_ids += 1
			self.instructions.append(i)

	def __eq__(self, __o: object) -> bool:
		return isinstance(__o, CFGNode) and __o.id == self.id
	
	def __str__(self) -> str:
		insts = "\n\t".join([str(i) for i in self.instructions])
		if self.label:
			return f"{self.label}:\n\t{insts}"
		else:
			return insts
		
	def to_x86(self) -> str:
		print(self.label)
		insts = "\n\n\t".join([i.to_x86() for i in self.instructions])
		if self.label:
			return f"{self.label}:\n\t{insts}\n"
		else:
			return insts
	
	def show_live(self):
		for i, inst in enumerate(self.instructions):
			logging.info(f"\t\t\t{self.live_before[i]}")
			logging.info(inst)
		logging.info(f"\t\t\t{self.live_out}")
	
class BranchNode(CFGNode):
	def __init__(self, id: int) -> None:
		super().__init__(id, NodeKind.BRANCH)
		self.true_branch: CFGNode = None
		self.false_branch: CFGNode = None
		self.merge: CFGNode = None
		self.condition = None

	def __str__(self) -> str:
		insts = "\n\t".join([str(i) for i in self.instructions])
		
		if self.false_branch:
			insts += f"\n\tje {self.false_branch.label}"
		else:
			insts += f"\n\tje {self.merge.label}"
		return f"{self.label}:\n\t{insts}\n"
		
	def to_x86(self) -> str:
		insts = "\n\t".join([i.to_x86() for i in self.instructions])
		if self.false_branch:
			insts += f"\n\tje {self.false_branch.label}"
		else:
			insts += f"\n\tje {self.merge.label}"
		return f"{self.label}:\n\t{insts}\n"

class NodeIdGen():
	count: int = 0

	@staticmethod
	def get_id():
		id_ = NodeIdGen.count
		NodeIdGen.count += 1
		return id_
	
class CFG():
	entry: CFGNode
	exit: CFGNode
	nodes: list[CFGNode]
	prog: str

	def __init__(self) -> None:
		self.nodes = []
		self.entry = self.new_node(kind=NodeKind.ENTRY)
		self.prog = ""

	def new_node(self, kind: NodeKind = NodeKind.STATEMENT, predecessor: CFGNode = None) -> CFGNode:
		node_id = NodeIdGen.get_id()
		if kind == NodeKind.BRANCH:
			n = BranchNode(node_id)
		else:
			n = CFGNode(node_id, kind)

		if predecessor:
			n.predecessors.append(predecessor)
			predecessor.successors.append(n)

		self.nodes.append(n)
		return n
	
	def edge(self, src: CFGNode, dst: CFGNode) -> None:
		if dst not in src.successors:
			src.successors.append(dst)
		if src not in dst.predecessors:
			dst.predecessors.append(src)
	
	def print_cfg(self, node: CFGNode, stop: CFGNode):
		if node == stop or node in self.visited:
			return
		self.visited.append(node)
		logging.info(str(node))

		if isinstance(node, BranchNode):
			self.print_cfg(node.true_branch, node.merge)
			if node.false_branch:
				self.print_cfg(node.false_branch, node.merge)
			self.print_cfg(node.merge, stop)
		else:
			for c in node.successors:
				self.print_cfg(c, stop)

	def to_x86(self, node: CFGNode, stop: CFGNode) -> str:
		if node == stop or node in self.visited:
			return
		self.visited.append(node)
		self.prog += node.to_x86()

		if isinstance(node, BranchNode):
			self.to_x86(node.true_branch, node.merge)
			if node.false_branch:
				self.to_x86(node.false_branch, node.merge)
			self.to_x86(node.merge, stop)
		else:
			for c in node.successors:
				self.to_x86(c, stop)

	def display(self):
		self.visited = []
		self.print_cfg(self.entry, self.exit)
		logging.info(self.exit)

	def print_x86(self):
		self.visited = []
		self.prog = ""
		self.to_x86(self.entry, self.exit)
		self.prog += self.exit.to_x86()
		return self.prog
	
	def display_liveness(self):
		for node in self.nodes:
			logging.info(f"Node: {node.label}")
			for i, ins in enumerate(node.instructions):
				logging.info(f"\t\t\t{node.live_before[i]}\n\t{ins}")
			logging.info(f"\t\t\t{node.live_before[-1]}\n")




class CFGBuilder():
	cur_node: CFGNode
	def __init__(self, _ast: AST) -> None:
		self.cfg = CFG()
		self.tree = _ast

	def build(self):
		self.tree = RemoveIntCasts().visit(self.tree)

		self.cur_node = self.cfg.new_node(predecessor=self.cfg.entry)

		self.to_cfg(self.tree)

		self.cfg.exit = self.cfg.new_node(kind=NodeKind.EXIT)

		self.clean_cfg()

	def clean_cfg(self):
		for node in self.cfg.nodes:
			if not node.successors:
				node.successors.append(self.cfg.exit)
				self.cfg.exit.predecessors.append(node)

	def to_cfg(self, node: AST):
		match node:
			case Module():
				for n in node.body:
					self.to_cfg(n)
			case Expr():
				if isinstance(node.value, Call):
					self.cur_node.append(node_to_ir(node))
			case Assign():
				self.cur_node.append(node_to_ir(node))
			case If():
				branch_node: BranchNode = self.cfg.new_node(NodeKind.BRANCH, predecessor=self.cur_node)
				branch_node.condition = node_to_ir(node.test)
				self.cur_node = branch_node
				self.cur_node.append(IR_Compare("", IR_Const(0), branch_node.condition))

				true_branch = self.cfg.new_node(predecessor=branch_node)
				branch_node.true_branch = true_branch
				false_branch = None
				merge_node = self.cfg.new_node()
				branch_node.merge = merge_node
				self.cfg.edge(self.cur_node, merge_node) # connect branch to merge even if there is no else
				
				if node.orelse:
					false_branch = self.cfg.new_node(predecessor=branch_node)
					branch_node.false_branch = false_branch
					self.cur_node = false_branch

					for i in node.orelse:
						self.to_cfg(i)
					self.cfg.edge(self.cur_node, merge_node)
				
				self.cur_node = true_branch
				for i in node.body:
					self.to_cfg(i)
				self.cur_node.append(IR_Jmp(merge_node.label))
				self.cfg.edge(self.cur_node, merge_node)

				self.cur_node = merge_node
			case While():
				while_condition: BranchNode = self.cfg.new_node(NodeKind.BRANCH, predecessor=self.cur_node)
				while_condition.condition = node_to_ir(node.test)
				while_condition.append(IR_Compare("", IR_Const(0), while_condition.condition))
				
				while_body = self.cfg.new_node(predecessor=while_condition)
				
				self.cur_node = while_body
				for i in node.body:
					self.to_cfg(i)
				self.cfg.edge(self.cur_node, while_condition)
				self.cur_node.append(IR_Jmp(while_condition.label))

				exit_while = self.cfg.new_node(predecessor=while_condition)
				
				while_condition.true_branch = while_body
				while_condition.false_branch = exit_while
				while_condition.merge = exit_while

				self.cur_node = exit_while
			case Return():
				self.cur_node.append(node_to_ir(node))
			case _:
				raise Exception(f"Unhandled node type in to_cfg, '{type(node)}'")

def build_cfg(_ast):
	logging.getLogger(__name__)
	builder = CFGBuilder(_ast)
	builder.build()
	return builder.cfg

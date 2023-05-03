class IR_Expr():
	pass

class IR_Var(IR_Expr):
	def __init__(self, name) -> None:
		self.name = name
	def __str__(self) -> str:
		return str(self.name)
	def __eq__(self, __o: object) -> bool:
		return isinstance(__o, IR_Var) and __o.name == self.name
	
class IR_Const(IR_Expr):
	def __init__(self, value) -> None:
		self.value = value
	def __str__(self) -> str:
		return f"${self.value}"
	def __eq__(self, __o: object) -> bool:
		return isinstance(__o, IR_Const) and __o.value == self.value

class IR_Instruction():
	def __init__(self) -> None:
		self.reads: set[str] = set()
		self.writes: set[str] = set()
		self.id = 0
		self.node_id = 0

	def __str__(self) -> str:
		raise NotImplementedError()
	def to_x86(self) -> str:
		raise NotImplementedError()
	def get_values(self) -> list[IR_Expr]:
		raise NotImplementedError()
	def update_rw(self):
		raise NotImplementedError()
	
class IR_Mov(IR_Instruction):
	def __init__(self, src: IR_Expr, dst: IR_Expr) -> None:
		super().__init__()
		self.src = src
		self.dst = dst

		assert isinstance(dst, IR_Var)

		self.writes.add(dst.name)
		if isinstance(src, IR_Var):
			self.reads.add(src.name)

	def __str__(self) -> str:
		return f"movl {self.src}, {self.dst}"
	
	def to_x86(self) -> str:
		if self.src != self.dst:
			return str(self)
		else:
			return ""
	def get_values(self):
		return [self.src]
	def update_rw(self):
		self.reads = set()
		self.writes = set()
		assert isinstance(self.dst, IR_Var)
		self.writes.add(self.dst.name)
		if isinstance(self.src, IR_Var):
			self.reads.add(self.src.name)
	
class IR_Call(IR_Instruction):
	func_map = {
		"print": "print_any",
	}
	def __init__(self, func: IR_Var, args: list[IR_Expr], dst: IR_Expr = None) -> None:
		super().__init__()
		self.func_name = func.name
		self.args = args
		self.dst = dst

		for a in args:
			if isinstance(a, IR_Var):
				self.reads.add(a.name)
				
		self.reads.add(func.name)
		
		if dst:
			assert isinstance(dst, IR_Var)
			self.writes.add(dst.name)

	def __str__(self) -> str:
		if self.dst:
			return f"{self.dst} = {self.func_name}({', '.join(str(a) for a in self.args)})"
		else:
			return f"{self.func_name}({', '.join(str(a) for a in self.args)})"
		
	def to_x86(self) -> str:
		ret = []
		ret.append("pushl %eax ## save caller-saved registers")
		ret.append("pushl %ecx ## save caller-saved registers")
		ret.append("pushl %edx ## save caller-saved registers")
		
		if self.func_name == "error_pyobj":
			ret.append(f"pushl $0")

			ret.append(
				f"call error_pyobj"
			)
			ret.append(f"addl $4, %esp")	
		else:
			i: int = len(self.args) - 1
			for arg in self.args[::-1]:
				# need to add '$'to the function pointer in create_closure!
				if i == 0 and (self.func_name == "create_closure"):
					arg = '$' + arg
				ret.append(f"pushl {arg}")
				i -= 1
				
			if (self.func_name[0] == '%'):
				ret.append(
				f"call *{self.func_name}"
				)
			else:
				ret.append(
				f"call {self.func_map.get(str(self.func_name), str(self.func_name))}"
				)
				

			if self.dst:
				ret.append(f"movl %eax, {self.dst}")

			if len(self.args) > 0:
				ret.append(f"addl ${len(self.args)*4}, %esp")

		ret.append("popl %edx ## restore caller-saved registers")
		ret.append("popl %ecx ## restore caller-saved registers")
		ret.append("popl %eax ## restore caller-saved registers")
		
		return "\n\t".join(ret)
	# for get values return a unique id since eval_input_int() doesnt evaluate to the same thing every time
	def get_values(self):
		return []
	def update_rw(self):
		self.reads = set()
		self.writes = set()
		for a in self.args:
			if isinstance(a, IR_Var):
				self.reads.add(a.name)
		if self.dst:
			assert isinstance(self.dst, IR_Var)
			self.writes.add(self.dst.name)

class IR_Binop(IR_Instruction):
	def __init__(self, op: str, src: IR_Expr, dst: IR_Expr) -> None:
		super().__init__()
		self.op = op
		self.src = src
		self.dst = dst

		assert isinstance(dst, IR_Var)

		self.writes.add(dst.name)
		self.reads.add(dst.name)

		if isinstance(src, IR_Var):
			self.reads.add(src.name)

	def __str__(self) -> str:
		return f"{self.op} {self.src}, {self.dst}"
	
	def to_x86(self) -> str:
		return str(self)
	def get_values(self):
		return [self.src]
	def update_rw(self):
		self.reads = set()
		self.writes = set()
		assert isinstance(self.dst, IR_Var)

		self.writes.add(self.dst.name)
		self.reads.add(self.dst.name)

		if isinstance(self.src, IR_Var):
			self.reads.add(self.src.name)
	
class IR_Unop(IR_Instruction):
	def __init__(self, op: str, dst: IR_Expr) -> None:
		super().__init__()
		self.op = op
		self.dst = dst

		assert isinstance(dst, IR_Var)

		self.writes.add(dst.name)
		self.reads.add(dst.name)

	def __str__(self) -> str:
		return f"{self.op} {self.dst}"
	
	def to_x86(self):
		if self.op == "not":
			ret = f"cmpl $0, {self.dst}"
			ret += f"\n\tje else_{self.node_id}_{self.id}"
			ret += f"\nif_{self.node_id}_{self.id}:"
			ret += f"\n\tmovl $0, {self.dst}"
			ret += f"\n\tjmp endif_{self.node_id}_{self.id}"
			ret += f"\nelse_{self.node_id}_{self.id}:"
			ret += f"\n\tmovl $1, {self.dst}"
			ret += f"\nendif_{self.node_id}_{self.id}:"
			return ret
		else:
			return f"{self.op} {self.dst}"
	def get_values(self):
		return [self.dst]
	def update_rw(self):
		self.reads = set()
		self.writes = set()
		assert isinstance(self.dst, IR_Var)

		self.writes.add(self.dst.name)
		self.reads.add(self.dst.name)
	
class IR_Compare(IR_Instruction):
	def __init__(self, op: str, src1: IR_Expr, src2: IR_Expr, dst: IR_Expr = None) -> None:
		super().__init__()
		self.op = op
		self.src1 = src1
		self.src2 = src2
		self.dst = dst

		if dst:
			assert isinstance(dst, IR_Var)
			self.writes.add(dst.name)

		if isinstance(src1, IR_Var):
			self.reads.add(src1.name)
		if isinstance(src2, IR_Var):
			self.reads.add(src2.name)

	def __str__(self) -> str:
		if self.dst:
			return f"{self.op} {self.src1}, {self.src2}, {self.dst}"
		else:
			return f"cmpl {self.src1}, {self.src2}"
		
	def to_x86(self):
		s = "sete" if self.op == "equals" else "setne"
		if self.dst:
			return f"cmpl {self.src1}, {self.src2}\n\t{s} %al\n\tmovzbl %al, %eax\n\tmovl %eax, {self.dst}"
		else:
			return f"cmpl {self.src1}, {self.src2}"
	
	def get_values(self):
		return [self.src1,self.src2]
	def update_rw(self):
		self.reads = set()
		self.writes = set()
		if self.dst:
			assert isinstance(self.dst, IR_Var)
			self.writes.add(self.dst.name)

		if isinstance(self.src1, IR_Var):
			self.reads.add(self.src1.name)
		if isinstance(self.src2, IR_Var):
			self.reads.add(self.src2.name)
		
class IR_Boolop(IR_Instruction):
	def __init__(self, op: str, src1: IR_Expr, src2: IR_Expr, dst: IR_Expr) -> None:
		super().__init__()
		self.op = op
		self.src1 = src1
		self.src2 = src2
		self.dst = dst

		if isinstance(src1, IR_Var):
			self.reads.add(src1.name)
		if isinstance(src2, IR_Var):
			self.reads.add(src2.name)
		
		assert isinstance(dst, IR_Var)
		self.writes.add(dst.name)

	def __str__(self) -> str:
		return f"{self.dst} = ({self.src1} {self.op} {self.src2})"
	
	def to_x86(self) -> str:
		ret = f"cmpl $0, {self.src1}"
		ret += f"\n\tje else_{self.node_id}_{self.id}"
		ret += f"\nif_{self.node_id}_{self.id}:"
		if self.op == "and":
			ret += f"\n\tmovl {self.src2}, {self.dst}"
			ret += f"\n\tjmp endif_{self.node_id}_{self.id}"
			ret += f"\nelse_{self.node_id}_{self.id}:"
			ret += f"\n\tmovl $0, {self.dst}"
		elif self.op == "or":
			ret += f"\n\tmovl {self.src1}, {self.dst}"
			ret += f"\n\tjmp endif_{self.node_id}_{self.id}"
			ret += f"\nelse_{self.node_id}_{self.id}:"
			ret += f"\n\tmovl {self.src2}, {self.dst}"
		else:
			raise Exception(f"Unknown boolop, '{self.op}'")
		ret += f"\nendif_{self.node_id}_{self.id}:"
		return ret

	def get_values(self):
		return [self.src1,self.src2]
	def update_rw(self):
		self.reads = set()
		self.writes = set()
		if isinstance(self.src1, IR_Var):
			self.reads.add(self.src1.name)
		if isinstance(self.src2, IR_Var):
			self.reads.add(self.src2.name)
		
		assert isinstance(self.dst, IR_Var)
		self.writes.add(self.dst.name)

class IR_Jmp(IR_Instruction):
	def __init__(self, target: str) -> None:
		super().__init__()
		self.target = target

	def __str__(self) -> str:
		return f"jmp {self.target}"
	def to_x86(self) -> str:
		return str(self)
	def get_values(self):
		return []
	def update_rw(self):
		pass

class IR_Return(IR_Instruction):
	def __init__(self, src: IR_Expr) -> None:
		super().__init__()
		self.src = src

		if isinstance(src, IR_Var):
			self.reads.add(src.name)

	def __str__(self) -> str:
		return f"return {self.src}"
	
	def to_x86(self) -> str:
		ret = f"movl {self.src}, %eax\n\t"
		ret += "popl %edi ## restore callee saved registers\n\t"
		ret += "popl %esi\n\t"
		ret += "popl %ebx\n\t"
		ret += "movl %ebp, %esp ## restore esp\n\t"
		ret += "popl %ebp ## restore ebp\n\tret"
		return ret
	def get_values(self):
		return [self.src]
	def update_rw(self):
		self.reads = set()
		self.writes = set()
		if isinstance(self.src, IR_Var):
			self.reads.add(self.src.name)
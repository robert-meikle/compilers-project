from IR.ir import *

from cfg import CFG, CFGNode, BranchNode

import logging
import json

def home(v, assignments: dict):
    if isinstance(v, IR_Const):
        return str(v)
    else:
        return assignments.get(str(v), str(v))


# takes a list of cfg_nodes,assignment
def assign_homes(cfg: CFG, assignments):
    """
    takes a cfg and assignments and returns x86 instructions
    """
    logging.getLogger(__name__)
    logging.info(f"Assignments\n-------------\n{json.dumps(assignments, indent=2)}")
    for node in cfg.nodes:
        if isinstance(node, BranchNode):
            node.condition = home(node.condition, assignments)
        for i in node.instructions:
            match i:
                case IR_Unop():
                    i.dst = home(i.dst, assignments)
                case IR_Return():
                    i.src = home(i.src, assignments)
                case IR_Mov() | IR_Binop():
                    i.src = home(i.src, assignments)
                    i.dst = home(i.dst, assignments)
                case IR_Compare() | IR_Boolop():
                    i.src1 = home(i.src1, assignments)
                    i.src2 = home(i.src2, assignments)
                    if i.dst:
                        i.dst = home(i.dst, assignments)
                case IR_Call():
                    if i.dst:
                        i.dst = home(i.dst, assignments)
                    i.args = [home(a, assignments) for a in i.args]
                    i.func_name = home(i.func_name, assignments)

    prog = cfg.print_x86()
    return prog

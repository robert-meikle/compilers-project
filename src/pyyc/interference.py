import logging
import json
from IR.ir import *

from cfg import CFG, CFGNode


class InterferenceGraph:
    def __init__(self, cfg, vars, function_names):
        self.cfg: CFG = cfg
        self.vars = vars
        self.function_names = function_names
        # adjacency matrix
        self.adj = {}

        # Initialize graph
        self.add_nodes()

    def add_nodes(self) -> None:
        """
        Initializes the graph by adding each variable from instructions.
        """
        # Add registers as nodes
        for r in ["%eax", "%ecx", "%edx", "%ebx", "%edi", "%esi"]:
            self.adj[r] = []

        # add variables as nodes
        for node in self.cfg.nodes:
            for inst in node.instructions:
                for v in inst.reads:
                    self.adj[v] = []
                for v in inst.writes:
                    self.adj[v] = []
        for f in self.function_names:
            self.adj.pop(f,None)
        logging.info(f"Vars:\n{json.dumps(self.adj, indent=2)}")


    def add_edge(self, src, dst) -> None:
        """
        Adds an edge between src and dst.
        """
        # Don't add edges to self
        if src == dst:
            return
        if src not in self.adj or dst not in self.adj:
            return
        # adding node to graph if it doesn't yet exist
        if not self.adj.get(src):
            self.adj[src] = []
        if not self.adj.get(dst):
            self.adj[dst] = []

        # Adding edge if it doesn't exist already
        if dst not in self.adj[src]:
            logging.debug(f"Adding edge {src} -> {dst}")
            self.adj[src].append(dst)

        # Add the opposite edge since not a di-graph
        if src not in self.adj[dst]:
            logging.debug(f"Adding edge {src} -> {dst}")
            self.adj[dst].append(src)

    def generate_graph(self):
        for node in self.cfg.nodes:
            for i, inst in enumerate(node.instructions):
                live_after = node.live_before[i + 1]
                # Target interferes with live after except source
                if isinstance(inst, IR_Mov):
                    for v in live_after:
                        if v != str(inst.src):
                            self.add_edge(str(inst.dst), v)
                # Target interferes will live after
                elif isinstance(inst, IR_Binop) or isinstance(inst, IR_Unop) or isinstance(inst, IR_Boolop):
                    for v in live_after:
                        self.add_edge(str(inst.dst), v)
                # Caller saved interfere with live after
                elif isinstance(inst, IR_Call):
                    for v in live_after:
                        for r in ["%eax", "%ecx", "%edx"]:
                            self.add_edge(v, r)
                    if inst.dst:
                        for v in live_after:
                            if v != str(inst.dst):
                                self.add_edge(str(inst.dst), v)
                elif isinstance(inst, IR_Compare):
                    for v in live_after:
                        if inst.dst:
                            self.add_edge(str(inst.dst), v)
                            self.add_edge("%eax", v)
                elif isinstance(inst, IR_Jmp):
                    pass
                elif isinstance(inst, IR_Return):
                    pass
                else:
                    raise Exception(
                        f"Unhandled case when generating interference graph, {inst}: {type(inst)}"
                    )

        # Logging
        for node in self.adj:
            logging.info(f"{node} -> {self.adj[node]}")
        logging.info("")

        return self.adj

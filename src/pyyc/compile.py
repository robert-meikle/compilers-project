import ast
import logging
import sys
from ast import AST, Module

from assign_homes import assign_homes
from cfg import build_cfg
from closure_conversion import closure
from explicate import explicate
from flatten import flatten
from graph_coloring import color_graph
from heapify import heapify
from interference import InterferenceGraph
from liveness import liveness_analysis
from spillcode import do_spill_code
from unify import unify_func_lambda
from uniquify import uniquify
from unparse import unparse
from util import add_parents, create_ast, get_function_defs
from type_checker import run_type_checker
from dispatch import dispatch

# optimization imports, currently unused
# from optimizations.dead_stores import dead_store_elim
# from optimizations.lvn import constant_folding, copy_folding, lvn

ASM_TEMPLATE = """{label}:
	pushl %ebp ## save caller's base pointer 
	movl %esp, %ebp ## set our base pointer 
	subl ${alloc}, %esp ## allocate for local vars
	pushl %ebx ## save callee saved registers
	pushl %esi
	pushl %edi
	{instructions}
"""
ASM_FOOTER = """popl %edi ## restore callee saved registers
	popl %esi
	popl %ebx
	movl $0, %eax ## set return value 
	movl %ebp, %esp ## restore esp
	popl %ebp ## restore ebp (alt. “leave”)
	ret ## jump execution to call site
"""

FLATPY_HEAD = """class Closure():
	def __init__(self, f, fr):
		self.f = f
		self.fr = fr
def get_free_vars(c):
	return c.fr
def get_fun_ptr(c):
	return c.f
def create_closure(f,fr):
	return Closure(f,fr)
def inject_big(s):
	return s

"""

function_names = {
    "is_int",
    "is_bool",
    "is_big",
    "is_function",
    "is_object",
    "is_class",
    "is_unbound_method",
    "is_bound_method",
    "inject_int",
    "inject_bool",
    "inject_big",
    "project_int",
    "project_bool",
    "project_big",
    "is_true",
    "print_any",
    "input_int",
    "input_pyobj",
    "eval_pyobj",
    "eval_input_pyobj",
    "create_list",
    "create_dict",
    "set_subscript",
    "get_subscript",
    "add",
    "equal",
    "not_equal",
    "create_closure",
    "get_fun_ptr",
    "get_free_vars",
    "set_free_vars",
    "error_pyobj",
    "print",
    "print_int_nl",
    "print_bool",
    "input_static",
}


# function => (name: str, args: list[str], cfg: CFG)
def compile_function(function):
    """
    Compiles an indiviual function.
    """
    func_name = function[0]
    func_args = function[1]
    cfg = function[2]

    cfg = liveness_analysis(cfg)
    cfg.display_liveness()

    # logging.info(f"\nOptimizations\n-----------------")
    ## Do optimizations here
    # for bb in cfg.nodes:
    # 	if len(bb.instructions):
    # 		bb_lvn = lvn(bb)
    # 		bb = constant_folding(bb, bb_lvn)
    # 		logging.info(f"\nconstant folded\n{bb}")
    #
    # 		bb = copy_folding(bb, bb_lvn)
    # 		logging.info(f"\ncopy folded\n{bb}")
    #
    # 		bb = dead_store_elim(bb)
    # 		logging.info(f"\ndead store eliminated\n{bb}\n*********")

    assignments = {}
    vars_ = set()
    complete = False
    unspillables = []

    while not complete:
        vars_.update(unspillables)
        # perform liveness analysis
        cfg = liveness_analysis(cfg)
        logging.info("\nLiveness\n-----------------")
        cfg.display_liveness()
        # generate the interference graph
        logging.info("\nInterference\n-----------------")
        interference_g = InterferenceGraph(cfg, vars_, function_names)
        # make func args interfere with eachother
        for i, arg in enumerate(func_args):
            for i, arg1 in enumerate(func_args):
                interference_g.add_edge(arg, arg1)
        graph = interference_g.generate_graph()

        logging.info("\nColoring\n-----------------")
        assignments = color_graph(graph, unspillables)

        logging.info("\nSpill Code\n-----------------")
        cfg, unspillables, complete = do_spill_code(cfg, assignments)

    alloc = len(unspillables) * 4

    instructions = assign_homes(cfg, assignments)
    # put func args in the proper registers TODO
    for i, arg in enumerate(func_args):
        if arg not in assignments:
            continue
        instructions = f"movl {8 + (4*i)}(%ebp), {assignments[arg]}\n\t" + instructions
    # we need to apply asm template here
    if func_name == "main":
        return (
            ".globl main\n"
            + ASM_TEMPLATE.format(
                label=func_name, alloc=alloc, instructions=instructions
            )
            + ASM_FOOTER
        )
    return ASM_TEMPLATE.format(label=func_name, alloc=alloc, instructions=instructions)


def log_ast(ast_: AST):
    """
    Unparses and prints the AST.  Prefers the builtin ast.unparse but sometimes
    it can fail so falls back on our custom unparse function.
    """
    try:
        logging.info(ast.unparse(ast_))
    except Exception:
        logging.info(unparse(ast_))


def compile_program():
    """
    Runs the compilation pipeline.
    """
    filename: str = sys.argv[1].rsplit(".", 1)[0]
    logging.info("Compile: %s\n----------", filename)

    logging.info("\nLex/Parse\n----------")
    ast_ = create_ast(sys.argv[1])
    log_ast(ast_)

    logging.info("\nType Checking\n----------")
    ast_ = run_type_checker(ast_, sys.argv[1])

    logging.info("\nDispatching\n----------")
    ast_ = dispatch(ast_)
    log_ast(ast_)

    logging.info("\nUniquify\n----------")
    ast_ = uniquify(ast_)
    log_ast(ast_)

    logging.info("\nUnify Defs/Lambdas\n----------")
    ast_ = unify_func_lambda(ast_)
    log_ast(ast_)

    logging.info("\nHeapify\n----------")
    ast_ = heapify(ast_)
    log_ast(ast_)

    logging.info("\nClosure Conversion\n----------")
    ast_ = closure(ast_)
    ast_ = add_parents(ast_)
    log_ast(ast_)

    logging.info("\nPre-Flatten\n----------")
    ast_ = flatten(ast_, [])
    ast_ = add_parents(ast_)
    log_ast(ast_)

    # Create .flatpy file
    # flatpy = unparse(ast_)
    # with open(f"{filename}.flatpy", "w", encoding="utf-8") as file_:
    #    file_.write(FLATPY_HEAD + flatpy)

    # logging.info("\nExplicate\n----------")
    # ast_ = explicate(ast_)
    # log_ast(ast_)

    logging.info("\nPost-Flatten\n----------")
    ast_ = flatten(ast_, [])
    log_ast(ast_)

    logging.info("\nBuild CFGs\n----------")
    function_defs = get_function_defs(ast_)
    functions = []
    # functions => list[(name: str, args: list[str], cfg: CFG)]
    for func_def in function_defs:
        name = func_def.name
        function_names.add(name)
        str_args = [arg_obj.arg for arg_obj in func_def.args.args]
        function_cfg = build_cfg(Module(func_def.body))
        functions.append((name, str_args, function_cfg))
        logging.info("Function: %s(%s)\n-----------------\n", name, str_args)
        function_cfg.display()

    logging.info("\nSelect Instructions\n----------")
    instructions = []
    for func in functions:
        instructions.append(compile_function(func))
    instructions_textual = "\n".join(instructions)
    logging.info(instructions_textual)

    with open(f"{filename}.s", "w", encoding="utf-8") as file_:
        file_.write(instructions_textual)

    return


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    logging.getLogger(__name__)

    if len(sys.argv) < 2:
        raise SyntaxError(f"Improper Usage: {sys.argv} <path to program to parse>.")

    compile_program()

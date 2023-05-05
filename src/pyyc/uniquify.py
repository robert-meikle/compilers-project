import ast
from ast import Name, Subscript, FunctionDef

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
	"print_bool_nl",
    "input_static",
    "int",
}


class Uniquify(ast.NodeTransformer):
    def __init__(self):
        # scope stack
        self.scopes = [{}]
        self.var_count = 0
        self.keywords = function_names
        self.already_done = []

    def defined_in_scope(self, var: str) -> str:
        """
        Checks if a var name is already defined in a scope, if so returns modified name.
        """
		
        if var in self.keywords:
            return var
        for scope in self.scopes[::-1]:
            if var in scope:
                return scope[var]
        print(var)
        return ""

    def add_definition(self, var: str) -> str:
        """
        Adds a new definition to the current scope, returns new name.
        """
        if var in self.keywords:
            return var
        if var in self.scopes[-1]:
            return var
        new_name = f"_{var}_{self.var_count}"
        self.scopes[-1][var] = new_name
        self.var_count += 1
        return new_name

    # assuming that test cases are syntactically correct code, every name should be defined already.
    # sets name to closest scope definition
    def visit_Name(self, node):
        node.id = self.defined_in_scope(node.id)
        return node

    def visit_Assign(self, node):
        # set scope for target var
        match node.targets[0]:
            case Name():
                _ = self.add_definition(node.targets[0].id)
            case Subscript():
                if isinstance(node.targets[0].value, Name):
                    _ = self.add_definition(node.targets[0].value.id)

        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        if node.name not in self.already_done:
            node.name = self.add_definition(node.name)

        # creates a new scope
        self.scopes.append({})

        for arg_obj in node.args.args:
            arg_obj.arg = self.add_definition(arg_obj.arg)

        self.generic_visit(node)

        # revert scope to parent
        _ = self.scopes.pop()
        return node

    def visit_Lambda(self, node):
        # creates a new scope
        self.scopes.append({})

        for arg_obj in node.args.args:
            arg_obj.arg = self.add_definition(arg_obj.arg)

        self.generic_visit(node)

        # revert scope to parent
        _ = self.scopes.pop()
        return node


def uniquify(ast_):
    uniquifyer = Uniquify()
    global_func_names = []
    for node in ast_.body:
        if isinstance(node, FunctionDef):
            global_func_names.append(uniquifyer.add_definition(node.name))
            node.name = global_func_names[-1]
            uniquifyer.already_done.append(node.name)

    return ast.fix_missing_locations(uniquifyer.visit(ast_))

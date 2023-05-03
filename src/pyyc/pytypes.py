class PyType:
    pass


class PyAny(PyType):
    def __str__(self) -> str:
        return "Any"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PyType)


class PyVoid(PyType):
    def __str__(self) -> str:
        return "None"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PyVoid)


class PyInt(PyType):
    def __str__(self) -> str:
        return "int"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PyAny) or isinstance(__value, PyInt)


class PyBool(PyType):
    def __str__(self) -> str:
        return "bool"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PyAny) or isinstance(__value, PyBool)


class PyList(PyType):
    def __init__(self, content_type: PyType) -> None:
        self.content_type = content_type

    def __str__(self) -> str:
        return f"list[{self.content_type}]"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PyAny) or (
            isinstance(__value, PyList) and self.content_type == __value.content_type
        )


class PyDict(PyType):
    def __init__(self, key_type: PyType, val_type: PyType) -> None:
        self.key_type = key_type
        self.val_type = val_type

    def __str__(self) -> str:
        return f"dict[{self.key_type},{self.val_type}]"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PyAny) or (
            isinstance(__value, PyDict)
            and self.key_type == __value.key_type
            and self.val_type == __value.val_type
        )


class PyFunc(PyType):
    def __init__(self, arg_types: list[PyType], return_type: PyType) -> None:
        self.arg_types = arg_types
        self.return_type = return_type

    def __str__(self) -> str:
        return " -> ".join([str(a) for a in self.arg_types]) + f" -> {self.return_type}"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PyAny) or (
            isinstance(__value, PyFunc)
            and len(self.arg_types) == len(__value.arg_types)
            and all(
                self.arg_types[i] == __value.arg_types[i]
                for i in range(len(self.arg_types))
            )
            and self.return_type == __value.return_type
        )

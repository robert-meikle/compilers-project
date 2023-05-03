nl: Callable[[int], int] = lambda x: (lambda y: x + y)(2)
print(nl(23))
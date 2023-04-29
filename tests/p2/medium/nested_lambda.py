nl: Callable[[int], Callable[[int], int]] = lambda x: lambda y: x + y
print(nl(23)(42))
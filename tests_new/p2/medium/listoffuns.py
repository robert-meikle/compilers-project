def sum(a: int, b: int) -> int:
    return a + b

def prod(a: int, b: int) -> int:
    return 0 if b == 0 else a + prod(a, b + -1)

def sub(a: int, b: int) -> int:
    return a + -b

x: list[Callable[[int,int], int]] = [sum, prod, sub]
print(x[0](1, 2))
print(x[1](1, 2))
print(x[2](1, 2))
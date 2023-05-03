def prod(a: int, b: int) -> int:
    return 0 if b == 0 else a + prod(a, b + -1)

print(prod(4, 3))
def f(x: int, y: int) -> bool:
    return x == y


z: bool = f(1, [1, 2, 3])
print(z)

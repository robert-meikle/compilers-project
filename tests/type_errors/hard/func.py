def f(x: int, y: int) -> int:
    return x + y


x = f
print(x(1, 2))
print(x(1, [1, 2, 3]))

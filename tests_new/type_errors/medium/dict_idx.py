x: dict[int, int] = {1: 2}
y: list[int] = [1, 2, x]
x[1] = y
print(x)

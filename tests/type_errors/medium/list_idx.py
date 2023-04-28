x: dict[int, int] = {1: 2}
y: list[int] = [1, 2, x]
y[2] = x[1]
print(y)

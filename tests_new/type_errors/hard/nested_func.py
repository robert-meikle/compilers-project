def f(x: int, y: int) -> bool:
    def f(x: int, y: list[int]) -> int:
        return x + y[0]

    return f(1, x + y) == 0


print(f(1, 2))

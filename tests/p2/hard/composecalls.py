def compose(f: Callable[[int], int], g: Callable[[int], int]) -> Callable[[int], int]:
    def _compose(x: int) -> int:
        return f(g(x))
    return _compose

def f(x: int) -> int:
    return x + 1

def g(x: int) -> int:
    return x + -1

print(compose(f, g)(23))
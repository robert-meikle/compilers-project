x: int = 7

def y() -> None:
    f = 7

def f() -> Callable[[int], int]:
    x: int = 2
    return lambda y: x + y

print(f()(3))
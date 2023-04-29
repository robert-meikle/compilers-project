f: Callable[[int], int] = lambda x: x

def use_f() -> Callable[[int], int]:
    return f

def create_f(f: Callable[[int], int]) -> Callable[[int], int]:
    return f

print(create_f(2))
print(use_f()(4))
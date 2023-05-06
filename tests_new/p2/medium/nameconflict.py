f: int= 1

def use_f() -> int:
    return f

def create_f(f: int) -> int:
    return f

print(create_f(2))
f = 4
print(use_f())
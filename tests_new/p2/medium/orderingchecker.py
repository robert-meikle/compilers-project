def callbefore(x: int) -> int:
    return x

x: int = 12
print(callbefore(x))

def callafter(x: int) -> int:
    return x

print(callafter(x))
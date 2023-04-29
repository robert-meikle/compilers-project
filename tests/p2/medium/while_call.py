def prod(a: int, b: int) -> int:
    return 0 if b == 0 else a + prod(a, b + -1)

def square(n: int) -> int:
    return prod(n, n)
    
i: int = 0
while square(i) != 25:
    i = i + 1
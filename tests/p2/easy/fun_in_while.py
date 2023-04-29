def add2sub1(a: int) -> int:
    return sub1(add2(a))

def add2(a: int) -> int:
    return a + 2

def sub1(a: int) -> int:
    return a + -1

x: int = 5
while(add2sub1(x) != 10):
    x = add2(x)

print(x)


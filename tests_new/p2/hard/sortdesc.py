def lessthan(a: int, b: int) -> bool:
    return True if a == 0 else False if b == 0 else lessthan(a + -1, b + -1)


def sort(l: list[int], len: int) -> list[int]:
    j: int = 0
    while j != len + -1:
        if lessthan(l[j], l[j + 1]):
            tmp: int = l[j]
            l[j] = l[j + 1]
            l[j + 1] = tmp
            j = -1
        else:
            x: int = 0
        j = j + 1
    return l


x: list[int] = [10, 11, 8, 9, 5, 4]
len: int = 6
print(sort(x, len))
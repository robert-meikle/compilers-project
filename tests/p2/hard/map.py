def map(f: Callable[[int], int], l: list[int], i: int, n: int) -> list[int]:
    return [f(l[i])] + map(f, l, i + 1, n) if i != n else []

print(map(lambda x: x + 1, [1,2,3,4], 0, 4))
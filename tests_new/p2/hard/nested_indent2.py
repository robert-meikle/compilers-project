def fun1() -> int:
    x: int = 1
    def fun2() -> int:
        x: int = 3
        def fun3() -> int:
            x: int = 5
            print(x)
            return x
        print(x)
        return fun3()
    print(x)
    return fun2()

print(fun1())
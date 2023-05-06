def fun(x: bool) -> bool:
    if x == True:
        return True
    else:
        return False

x: int = 10 if fun(bool(input())) else 20
print(x)

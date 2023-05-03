def while_in_fun(x: int, y: int) -> int:
    while(x != y):
        x = x + 1
    return x

print(while_in_fun(eval(input()), eval(input())))
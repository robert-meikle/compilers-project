def is_true(x: int) -> bool:
    return x == True

def true_fun() -> bool:
    return True

if is_true(eval(input())):
    print(true_fun())
else:
    print(not true_fun())
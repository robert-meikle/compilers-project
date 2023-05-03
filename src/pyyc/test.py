class Closure:
    def __init__(self, f, fr):
        self.f = f
        self.fr = fr


def get_free_vars(c):
    return c.fr


def get_fun_ptr(c):
    return c.f


def create_closure(f, fr):
    return Closure(f, fr)


def inject_big(s):
    return s


def closure_0(free_vars__fib_0, _n_1):
    tmp1 = 0
    tmp2 = _n_1 == tmp1
    tmp0 = 0
    if not tmp2:
        tmp4 = 1
        tmp5 = _n_1 == tmp4
        tmp3 = 1
        if not tmp5:
            tmp6 = inject_big(_fib_0)
            tmp7 = get_free_vars(tmp6)
            tmp8 = 1
            tmp9 = -tmp8
            tmp10 = _n_1 + tmp9
            tmp11 = inject_big(_fib_0)
            tmp12 = get_fun_ptr(tmp11)
            tmp13 = tmp12(tmp7, tmp10)
            tmp14 = inject_big(_fib_0)
            tmp15 = get_free_vars(tmp14)
            tmp16 = 2
            tmp17 = -tmp16
            tmp18 = _n_1 + tmp17
            tmp19 = inject_big(_fib_0)
            tmp20 = get_fun_ptr(tmp19)
            tmp21 = tmp20(tmp15, tmp18)
            tmp22 = tmp13 + tmp21
            tmp3 = tmp22
        tmp0 = tmp3
    return tmp0


tmp23 = []
_fib_0 = create_closure(closure_0, tmp23)
tmp24 = inject_big(_fib_0)
tmp25 = get_free_vars(tmp24)
tmp26 = inject_big(_fib_0)
tmp27 = get_fun_ptr(tmp26)
tmp28 = tmp27(tmp25, 6)
print(tmp28)

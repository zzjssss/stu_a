from functools import wraps


def my_count_calls(ack:str):

    def count_calls(func):
        a: int = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal a
            a += 1
            print(f"Call {a} of {func.__name__}")
            return func(*args, **kwargs)

        return wrapper
    return count_calls


@my_count_calls("first")
def test():
    pass

# 请实现该装饰器

@my_count_calls("second")
def hello():
    pass


a= test
b = test   # 这样是一个wrapper！ 会共享一个对象
a()
b()
#不想共享一个对象就用装饰器工厂直接
c = my_count_calls("c")(test.__wrapped__)
d = my_count_calls("d")(test.__wrapped__)
c()
d()

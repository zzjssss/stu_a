from functools import wraps


def lizi(func):
    print("修饰头")
    @wraps(func)
    def wrapper(*args,**kwargs):
        print("修饰体")
        #触发函数位置
        res = func(*args,**kwargs)
        return res
    return wrapper



@lizi
def say_hello():
    print("say hellow")



say_hello()
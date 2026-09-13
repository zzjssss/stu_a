from functools import wraps
from logging import DEBUG
import re

#有参数修饰器

from pydantic import validate_call

@validate_call
def my_instance(level):
    def validates_call(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            print(level)
            res  =  func(*args,**kwargs)
            return res
        return wrapper
    return validates_call

def all_extract_number(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        for arg in args:
            # 提取单个数字并拼接，例如 '1,2' -> '12'
            digits_in_arg = "".join(re.findall(r"\d+", str(arg)))
            new_args.append(digits_in_arg)

        print(f"各参数提取后的结果: {new_args}")
        # 将处理后的参数列表解包传回原函数
        res = func(*new_args, **kwargs)
        return res

    return wrapper





@my_instance(level="INFO")
@all_extract_number
@validate_call
def instance(a:int|str,b:int|str,c:int|str):
    print(f"{a} - {b} - {c}")




a1 = input("请输入第一个数：")
a2 = input("请输入第二个数：")
a3 = input("请输入第三个数：")
instance(a1,a2,a3)


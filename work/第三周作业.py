from functools import wraps
from typing import TypeVar, Callable

from pydantic import validate_call


def str_for_dict(func):
    @wraps(func)
    def wrapper(*args):
        list_s = list(args[0])
        list_dict = {a:list_s.count(a) for a in set(list_s)}
        print(f"字符串内各个字符的统计{list_dict}")
        return func(list_dict)
    return wrapper




"""
@validate_call
def str_for_dict(st:str)->dict[str,int]:
    list_str =list(st)
    return  {a:list_str.count(a) for a in set(list_str)}

"""

@str_for_dict
@validate_call
def count_char(list_q_instance :dict[str,int])->dict[str,int] :
    dict_char = {"letter":0, "digit":0, "space":0, "other":0}

    for chart, numt in list_q_instance.items():
        if chart.isalpha():
            dict_char["letter"] += numt
        elif chart.isdigit():
            dict_char["digit"] += numt
        elif chart.isspace():
            dict_char["space"]  += numt
        else:
            dict_char["other"] += numt
    return dict_char


#test----

s: str = input("输入字符串")
print(count_char(s))




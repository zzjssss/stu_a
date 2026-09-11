"""输入一批正整数(用空格隔开)
，输出它们的次大值、次小值，次大值的阶乘，
次大值与次小值的最大公约数、最小公倍数。"""
import math
from math import lgamma


def work_thirt(strs: str):

    list_sorted = sorted(list(map(int, strs.split())))
    print(list_sorted)
    second_max_min_god = math.gcd(list_sorted[-2], list_sorted[1])

    """   """
    print(f"次大值{list_sorted[-2]}、次小值{list_sorted[1]}、次大值的阶乘{math.factorial(list_sorted[-2])}")
    print(f"次大值与次小值的最大公约数{second_max_min_god}、最小公倍数{list_sorted[-2]*list_sorted[1]//second_max_min_god}")


# test  1 2 3 4 5 6 7 8 9 11 3333
try:
    work_thirt(input("输入一组数据"))
except Exception as e:
    print(e)
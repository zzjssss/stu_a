# 输入一批数据(用空格隔开)，输出它们的个数、最大值、最小值、均值、方差、标准差。

import math


def second_work(strs: str):
    str_list = strs.split()
    list_data = list(map(float, str_list))
    data_lent = len(list_data)
    data_sum = sum(list_data)
    data_mean = data_sum / data_lent
    data_var = sum((i - data_mean) ** 2 for i in list_data) / data_lent
    print(
        f"个数{len(list_data)}、最大值{max(list_data):.3f}、最小值{min(list_data):.3f}、\n\
        均值{data_mean:.3f}、方差{data_var:.3f}、标准差{math.sqrt(data_var):.3f}")


try:  # test 1 1.1 1.3 1.4 8.8 5.6 7.7
    strs = input("请输入数据集合：")
    second_work(strs)
except Exception as e:
    print(f"{e} - ErrorName:{type(e)}")
finally:
    print("The end")

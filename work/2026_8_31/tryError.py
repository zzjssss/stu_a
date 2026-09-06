#  输入数字  获取对于的天数

import logging
from calendar import weekday

my_logging = logging.getLogger("My_Debug_Logging")
my_logging.setLevel(logging.DEBUG)
formation = logging.Formatter("%(asctime)s--%(levelname)s--%(message)s")
console = logging.StreamHandler()
#filr = logging.FileHandler("test.txt")
console.setFormatter(formation)
my_logging.addHandler(console)


class My_Except(Exception):
    def __init__(self,day):
        self.day = day
    def __str__(self):
        return f"输入不在范围内的数值:{self.day}，请输入0-6  _  "

week_dirt = {
    1: "星期一",
    2: "星期二",
    3: "星期三",
    4: "星期四",
    5: "星期五",
    6: "星期六",
    0: "星期天"
}
"""
while 1:
    try:
        day= int(input("输入0-6  _  :"))
        if day not in week_dirt:
            raise My_Except(day)

        print(f"今天是{week_dirt[day]}")
        break
    except My_Except as e:
        my_logging.debug("debug 业务异常 输入范围错误")
        print(e)
    except ValueError:
        my_logging.info("info  业务异常 输入数值类型错误")
        print("请输入数字，谢谢")


写法
检查什么
示例
key in dict
key 是否存在
1 in week_dirt → True


value in dict.values()
value 是否存在
"星期一" in week_dirt.values() → True


(k,v) in dict.items()
key-value 配对是否存在
(1,"星期一") in week_dirt.items() → True


"""











while 1:
    try:
        day = int(input("输入0-6的数字输出对应的xxxx"))
        if day not in week_dirt:
            raise My_Except("输入的不是xxxx")
        print(f"今天是{week_dirt[day]}")
    except My_Except as e:
        print(e)
    except Exception as e:
        print(e)
















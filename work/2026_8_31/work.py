"""
name=input("输入人名")
country=input("输入国家")
print(f"世界那么大，{name}想去{country}国家看看")


def sum(a):
    if a ==1 :
        return 1
    else:
        return int(a)+sum(a-1)


result=sum(100)
print(f"1加到100{result}")





week_day={
    1:"monday",
    2:"Tuesday",
    3:"Wednesday",
    4:"Therapy",
    5:"Friday",
    6:"Saturday",
    0:"Sunday",
}
while True:
    day: int=int(input("输入0-6 输出对应星期"))
    if day in week_day:
        print(f"今天是{week_day[day]}")
        break
    else:
        print("输入错误,请重新输入")
"""
week_day={
    1:"monday",
    2:"Tuesday",
    3:"Wednesday",
    4:"Therapy",
    5:"Friday",
    6:"Saturday",
    0:"Sunday",
}

class DayInputError(Exception):
    def __init__(self, day):
        self.day = day
    def __str__(self):
        return f"输入错误: {self.day} 不在0-6范围内，请重新输入"

while True:
    try:
        day: int=int(input("输入0-6 输出对应星期"))
        if day not in week_day:
            raise DayInputError(day)
        print(f"今天是{week_day[day]}")
        break
    except DayInputError as e:
        print(e)
    except ValueError:
        print("请输入有效的整数")
"""

import turtle
import math

l=200
r=l*2/(3+5**0.5)
x=l/(2+5**0.5)

turtle.begin_fill()
turtle.pensize(15)
turtle.pencolor("yellow")
turtle.fillcolor("yellow")
for i in range(5):
    turtle.forward(l)
    turtle.right(144)

turtle.forward(r)
for i in range(5) :
    turtle.forward(x)
    turtle.right(144/2)
turtle.end_fill()
turtle.mainloop()
"""
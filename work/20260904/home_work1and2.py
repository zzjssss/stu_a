
""""

a = "a"
b = 5
c = a*b
print(c)

#不使用第三个变量，交换 x = 10 和 y = 20 的值，写出至少两种方式。
x = 10
y=20
x,y=y,x
print(x,y)
"""
from os.path import split

"""
编写程序，输入一个分数（0-100），输出对应等级：
90-100 → A
80-89 → B
70-79 → C
60-69 → D
0-59 → 不及格
其他 → 输入不合法
要求：使用 if-elif-else 和 match-case 各写一遍

def score(sc):
    if 100>= sc >=90:
        print("A")
    elif 89>=sc>=80:
        print("B")


s = "Hello Python World"
str=s.split(" ")
# 用——拼接
print(s[::-1])
"""

scores = [
    {"name": "张三", "score": 85},
    {"name": "李四", "score": 92},
    {"name": "王五", "score": 68},
    {"name": "赵六", "score": 73},
    {"name": "孙七", "score": 55},
]

# (3) 找出最高分和最低分对应的学生姓名
print(f"最高分组：{max(scores,key=lambda s:s.get("score",0))}")
print(f"最低分组：{min(scores,key = lambda s:s.get("score",0))}")

# (4) 按分数从高到低排序后输出排名（格式：第1名：李四 92分）
print(sorted(scores,key= lambda s : s.get("score"),reverse=True)[::1])


"""

my_tags = {"python", "agent", "fastapi", "mcp"}
peer_tags = {"python", "langgraph", "fastapi", "rag"}


# 完成：共用标签、仅我独有标签、合并后的总标签数  set
print(my_tags & peer_tags)
print(f"{my_tags - peer_tags}and{peer_tags - my_tags}")
print(my_tags | peer_tags)



#按「总额」从高到低打印前 3 位销售（用 Python 惯用写法排序）：

sales = [
    {"name": "A", "amount": 320},
    {"name": "B", "amount": 150},
    {"name": "C", "amount": 400},
    {"name": "D", "amount": 210},
    {"name": "E", "amount": 99},
]

print(sorted(sales,key = lambda s:s.get("amount",0),reverse=True)[:3])
# 在这里补：一个内部函数 count()，每次调用 +1 并返回
def make_counter(start=0):
    num = start
    def count():
        nonlocal num
        num+=1
        return num
    return count

c = make_counter(5)
print(c())   # 6
print(c())   # 7

"""

def Function_a(num = 0):
    local_num = num
    def Nei_cen():
        nonlocal local_num
        local_num+=1
        return local_num
    return Nei_cen


scp = Function_a(5)
print(scp())
print(scp())
#闭包本质上就是一种"轻量级的类
"""
能不能详细解释，听不懂，为什么函数内的值会持久存在
，是因为赋值给了外部的c，c是调用函数处的变量，所以含有被调用函数的属性吗，
那是不是能理解成我创建了一个类，类的属性被类方法调用，我创建一个这个类，
那这个类的属性也就具有持久性了，
不会因为使用了类方法调用类属性导致类属性被重置

你的理解完全正确！闭包本质上就是一种"轻量级的类"。让我详细解释。
"""


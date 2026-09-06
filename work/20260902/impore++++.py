


# 就是靠 列表推导式 写出  [[1,0,0],[0,1,0],[0,0,1]]   特殊result8 = [[0] * i + [1] + [0] * (2 - i) for i in range(3)]
result= [ [1*(i==j) for j in range(3)]for i in range(3)]
print(result)


#
# ===== 第10题：综合题 =====
# 把 students 按分数分为 "及格" 和 "不及格" 两组
# 期望: {'及格': ['小明', '小刚', '小美'], '不及格': ['小红', '小强']}


students = [
    {"name": "小明", "score": 85},
    {"name": "小红", "score": 52},
    {"name": "小刚", "score": 90},
    {"name": "小美", "score": 60},
    {"name": "小强", "score": 44},
]

result2= {f"{judge}":[stu.get("name",None) for stu in students if((stu.get("score",0)>=60)== (judge=="pass"))]for judge in ["pass","flunk"]}
print(result2)

#result  [[1, 0, 0], [0, 1, 0], [0, 0, 1]]   {'pass': ['小明', '小刚', '小美'], 'flunk': ['小红', '小强']}

# ========== 列表推导式练习题 ==========
# 每道题先自己写，再展开看答案

# --- 基础数据 ---
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
names = ["alice", "BOB", "charlie", "DAVE"]
words = ["hello", "world", "python", "code"]
students = [
    {"name": "小明", "score": 85},
    {"name": "小红", "score": 52},
    {"name": "小刚", "score": 90},
    {"name": "小美", "score": 60},
    {"name": "小强", "score": 44},
]

try:
    # ===== 第1题：基础遍历 =====
    # 把 numbers 中每个数乘以 2
    # 期望: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    result1 = [n * 2 for n in numbers]  # 在这里写  [n for n in numbers*2 ]  就变成了两个数组

    # ===== 第2题：带条件过滤 =====
    # 找出 numbers 中所有的偶数
    # 期望: [2, 4, 6, 8, 10]
    result2 = [n for n in numbers if n % 2 == 0]  # 在这里写

    # ===== 第3题：字符串处理 =====
    # 把 names 中所有名字转为大写
    # 期望: ['ALICE', 'BOB', 'CHARLIE', 'DAVE']
    result3 = [n.upper() for n in names]  # 在这里写

    # ===== 第4题：带条件的字符串操作 =====
    # 找出 names 中名字长度大于 3 的，并转为大写
    # 期望: ['ALICE', 'CHARLIE']
    result4 = [n.upper() for n in names if len(n) > 3]  # 在这里写

    # ===== 第5题：f-string 格式化 =====
    # 把 words 中每个单词变成 "单词:长度" 的格式
    # 期望: ['hello:5', 'world:5', 'python:6', 'code:4']
    result5 = [{f"单词：{w}": f"长度：{len(w)}"} for w in words]

    # ===== 第6题：字典列表操作 =====
    # 提取 students 中所有及格（score >= 60）的学生名字
    # 期望: ['小明', '小刚', '小美']
    result6 = [stu.get("name", None) for stu in students if stu.get("score", 0) >= 60]


    # ===== 第7题：字典列表 + 格式化 =====
    # 把及格的学生格式化为 "名字(分数)" 的形式
    # 期望: ['小明(85)', '小刚(90)', '小美(60)']
    result7 = [f"{stu.get("name", None)}({stu.get("score", None)})" for stu in students if
               int(stu.get("score", 0)) >= 60]


    # ===== 第8题：嵌套列表推导式（进阶）=====
    # 生成一个 3x3 的单位矩阵（对角线为1，其余为0）
    # 期望: [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    result8 =  [[1*(i==j) for j in range(3)] for i in range(3)]


    # [[1 if i== j else 0 for j in range(3)] for i in range(3)]

    # ===== 第9题：字典推导式 =====
    # 用 numbers 生成字典 {数: 数的平方}，只要 1~5
    # 期望: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
    result9 = {f"{nus}":f"{nus*nus}" for nus in numbers if 5 >= nus >= 1}


    # ===== 第10题：综合题 =====
    # 把 students 按分数分为 "及格" 和 "不及格" 两组
    # 期望: {'及格': ['小明', '小刚', '小美'], '不及格': ['小红', '小强']}
    result10 =  {f"{a}":[ku.get("name",None) for ku in students if((ku.get("score",0)>=60) == (a=="及格"))] for a in ["及格","不及格"]}
    print(result10)
    #"及格":[], "不及格":[]
    """
    """
except Exception as e:
    print("之错误")


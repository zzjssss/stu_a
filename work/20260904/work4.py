"""
第四题：推导式专项（易错点）
--------------------------------------------------------
(1) 用列表推导式生成 1~20 中所有能被 3 整除但不能被 5 整除的数

(2) 用字典推导式将以下列表转换为 {姓名: 分数} 的字典：
    students = [("张三", 85), ("李四", 92), ("王五", 68)]

(3) 【陷阱题】以下代码的输出是什么？请先写出你的预测，再运行验证。
    注意：这里涉及链式比较运算符的优先级问题。

    result = {x: x > 3 < 8 for x in range(6)}
    print(result)

    提示：Python 中 a > b < c 等价于 (a > b) and (b < c)，
          但在推导式中行为可能不同，请仔细分析。

(4) 用推导式从以下字典列表中统计每个 grade 出现的次数，
    排除 grade 为 None 的记录：
    data = [
        {"name": "A", "grade": "优"},
        {"name": "B", "grade": "良"},
        {"name": "C", "grade": None},
        {"name": "D", "grade": "优"},
        {"name": "E", "grade": "良"},
        {"name": "F", "grade": "优"},
    ]
    期望输出：{"优": 3, "良": 2}
"""

data = [
    {"name": "A", "grade": "优"},
    {"name": "B", "grade": "良"},
    {"name": "C", "grade": None},
    {"name": "D", "grade": "优"},
    {"name": "E", "grade": "良"},
    {"name": "F", "grade": "优"},
]

a = [g.get("grade") for g in data if g.get("grade") is not None]
print(a)
cd ={g:a.count(g) for g in set(a)}
print(cd)


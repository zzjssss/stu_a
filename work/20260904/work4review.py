cities = [("北京", 32), ("上海", 28), ("广州", 35), ("深圳", 30)]

print([a for a in range(50) if a%4 == 0 and a %6 !=0])
data = [
    {"id": 1, "level": "高"},
    {"id": 2, "level": "低"},
    {"id": 3, "level": None},
    {"id": 4, "level": "中"},
    {"id": 5, "level": "高"},
    {"id": 6, "level": "低"},
    {"id": 7, "level": "高"},
    {"id": 8, "level": None},
]
sertt = [a.get("level") for a in data if a.get("level") is not None]
pp = {b:sertt.count(b) for b in set(sertt)}
print(pp)


matrix = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
print([x for raw in matrix for x in raw])

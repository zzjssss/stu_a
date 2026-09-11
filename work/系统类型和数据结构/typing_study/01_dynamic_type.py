import copy
# 动态类型的本质
"""
list_dict= [
    {"name": "A", "amount": 320},
    {"name": "B", "amount": 150},
    {"name": "C", "amount": 400},
    {"name": "D", "amount": 210},
    {"name": "E", "amount": 99},
]

a = copy.copy(list_dict)
b = copy.deepcopy(list_dict)
print(a)
a[0]["name"]= "AA"
# 会发现   原被copy的 复合类型也变化了    copy 没有把list内的dict
#  一起船舰一个新的对象 ，  只创建 了新的list  外层


print(b)
b[0]["name"]= 1
print(a+b)
"""

print("=" * 66)






def total(nums:list[int] | None):              # 故意不写注解
    s = 0
    for n in nums:
        s += n
        print(n)
        # 混进字符串时，这里才炸
    return s
print(total([1,2,3,4,2]))



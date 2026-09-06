"""
(1) 编写函数 count_words(text)，统计一段文本中每个单词出现的次数，
    返回一个字典 {单词: 次数}，忽略大小写。
    示例：count_words("Hello hello World") → {"hello": 2, "world": 1}

(2) 编写函数 add_student(name, grade, students=None)，
    将 {"name": name, "grade": grade} 添加到 students 列表中。
    注意：必须正确处理默认参数，避免可变默认参数陷阱。
    调用示例：
      add_student("小明", 90)   → [{"name": "小明", "grade": 90}]
      add_student("小红", 85)   → [{"name": "小红", "grade": 85}]
      （每次不传 students 时应返回只含当前一条记录的新列表）
"""


def count_words(text:str)->dict:
    text = text.upper()
    work = text.split(" ")
    result ={}
    for w in work:
        result[w] = result.get(w,0) +1
    return result
def add_student(name, grade, students=None):
    if students is None:
        students = []
    students.append({"name":name,"grade":grade})

    return students


print(count_words("Hello hello World"))
print(add_student("小明", 90,[{"name":1,"grade":111}]))
"""
B1. 写一个函数 word_count(text: str) -> dict，返回每个单词出现次数。要求：

全部转小写
去掉标点（只保留字母和可能的撇号）
返回 {单词: 次数}
"""
import json


def word_count(text: str) -> dict:
    str_s= ""
    aka=[]
    text = text.lower()
    for ch in text:
        if ch.isalpha() or ch.isspace() or ch =="'" or ch==" ":
            str_s += ch
    aka = str_s.split(" ")
    text_dict = {a:aka.count(a) for a in set(aka)}
    return text_dict


wc = word_count("Hello world! hello, Python. world world?")
print(wc)





"""
 写一个函数 ，
 从一个 {单词: 次数} 字典中取出出现次数最多的前 n 个，
 返回形如 [("the", 10), ("and", 8)] 的列表（按次数从高到低）。
 提示：可用 sorted 配合 dict.items()
"""

def top_n_counts(d: dict, n: int) -> list:
    akaa =sorted(d.items(), key=lambda s:s[1],reverse=True)[:n:]
    return akaa

result =top_n_counts(wc, 1)
print(result)


# json数据 与 dict    之间的转换
# json.dumps()  dict 转为 json
# json.loads()  json 转为 dict
json_str='{"name":"zhangsan","age":18}'
pyton_dict= json.loads(json_str)
print(type(pyton_dict))

json_str_upload= json.dumps(pyton_dict)
print(type(json_str_upload))


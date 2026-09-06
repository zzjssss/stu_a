scores = [
      {"name": "张三", "score": 85},
      {"name": "李四", "score": 92},
      {"name": "王五", "score": 68},
      {"name": "赵六", "score": 73},
      {"name": "孙七", "score": 55},
  ]

#(1) 筛选出及格（score >= 60）的学生，输出姓名和分数

stu = [s.get("name") for s in scores if s.get("score",0)>=60 ]
#['张三', '李四', '王五', '赵六']

#计算全班平均分（保留一位小数）
sum_fen =sum([s.get("score",0) for s in scores])  / len(scores)
#print(format(sum_fen,".1f"))

#(3) 找出最高分和最低分对应的学生姓名
score_max = max(scores,key=lambda s:s.get("score",0))
# max  换成min
print(score_max)

# 从高到低  输出
scores_sorted_order=sorted(scores,key=lambda s:s.get("score",0),reverse=True)[::1]
# 从低到高
scores_sorted_resverord= sorted(scores,key= lambda s:s.get("score",0),reverse=True)[::-1]

print(scores_sorted_order)
print(scores_sorted_resverord)

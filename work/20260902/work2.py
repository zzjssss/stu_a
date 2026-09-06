scores = [82, 95, 60, 71, 100, 45, 88]

passedNames = [f"{a}分及格" for a in scores if a >= 60 ]

result = ",".join(passedNames)
print(result)
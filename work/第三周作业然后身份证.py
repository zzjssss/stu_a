from datetime import datetime

sfz = input("请输入身份证号")
sex=["男","女"]
year = datetime.now().year
print(f"你经年：{year-int(sfz[6:10])}岁了 是{sex[1 - int(sfz[16]) % 2]}")
print(sfz[16])  #奇数男   偶数女

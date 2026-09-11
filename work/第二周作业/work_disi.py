
#输入一批数据(用空格隔开)，输出它们的中位数。
def work_disi(strs: str):
    strs_list = strs.split()
    strs_list = sorted(list(map(float, strs_list)))
    strs_len=len(strs_list)
    if strs_len %2 == 0 :
        print("数据集个数为偶数 将输出一个中位数")
        print(f"中位数：{(strs_list[strs_len//2 -1] +strs_list[strs_len//2 ])/2:.3f} -- 和")
    else:
        print("数据集个数为奇数 将输出一个中位数")
        print(f"中位数：{strs_list[strs_len//2]:.3f}")
    print(f"{'*'*6}--计算函数结束--{'*'*6}{"\n"}")


#test：
#work_disi("1.1   5.5 4.2 6.6 2.3 3 4 56") #偶数
#work_disi("1.1   5.5 4.2 6.6 2.3 3 4 56 7") #奇数
work_disi(input("输入数据集："))

math.phi
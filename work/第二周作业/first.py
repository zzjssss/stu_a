import math as m

while True:
    try:
        user_input = input("输入一个实数")
        x = float(user_input)
    except ValueError:
        print("输入错误，请重新输入")
    else:

        abs_x = abs(x)
        print(f"\n绝对值 ：{abs_x} --绝对值平方根：{round(m.sqrt(abs_x), 2)}  --e(x)：{round(m.exp(x), 2)}\n\
            --sin(x+pi/4)：{round(m.sin(x + m.pi / 4), 2)} --log10(|x|)：{round(m.log10(abs_x), 2)}\n\
            --向上取整：{m.ceil(x)}  --向下取整：{m.floor(x)}--整数部分：{int(x)}")
        break

print("输入完毕")






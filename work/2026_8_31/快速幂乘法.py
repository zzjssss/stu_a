def My_pow(base: int, power: int) -> int:
    result = 1
    while power > 0:
        if power % 2 == 1:
            result *= base
        base*=base
        power //= 2  # 二进制右移一位
    return result
print(My_pow(2, 3))
def bad_add(item: str, box: list = []) -> list:   # PyCharm 会警告，这个警告是对的！
    box.append(item)
    return box


print(bad_add("a"))
print(bad_add("b"))  # 会累计     此为 函数默认参数陷阱

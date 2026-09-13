def add(a: int, b: int) -> int:
    return a + b

add(1, 2)        # ✓ 正常
add("1", 2)      # ✗ 传了字符串
add(1, 2, 3)     # ✗ 参数多了
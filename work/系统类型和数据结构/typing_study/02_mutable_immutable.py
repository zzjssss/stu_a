

import copy
import time
from typing import Any


#  可变与不可变
IMMUTABLE_EXAMPLES: tuple[Any, ...] = (
    1, 3.14, True, None, "abc", (1, 2), frozenset({1, 2}), b"bytes",
)
MUTABLE_EXAMPLES: tuple[Any, ...] = (
    [1], {1, 2}, {"k": 1}, bytearray(b"ab"),
)

def is_Hasi(obj:Any)->bool:
    try:
        hash(obj)   # 判断是否有哈希值
        return True
    except Exception as e:
        return False
print(is_Hasi((1,0)))

print(frozenset([1,2,3]))   # 冻结集合
"""def make_counter():
    count = 0
    def Count():
        nonlocal count
        count += 1
        return count
    return Count
c=make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3


"""


import typing


@typing.runtime_checkable
class Duck(typing.Protocol):
    def fly(self):...


class Chinese:
    def fly(self):
        print("中国人 can fly")

a = Chinese()
a.fly()
print(f"isinstance_Duck?:{isinstance(a,Duck)} ")











import typing


@typing.runtime_checkable
class Duck(typing.Protocol):
    def fly(self):...

class Birt :
    def __init__(self,str= None):
        self.str=str
    def __str__(self):
        return self.str

    def fly(self):
        if self.str is None:
            self.str="i am a Birt"
        print(f"i am a Birt and{self.str}")

print(issubclass(Birt,Duck))
print(Birt("中国人能飞"))
p = Birt()
print(isinstance(p,Duck))
p.fly()
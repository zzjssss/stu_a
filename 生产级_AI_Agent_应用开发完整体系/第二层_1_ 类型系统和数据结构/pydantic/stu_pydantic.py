from pydantic import BaseModel
import typing


@typing.runtime_checkable
class Duck_Basic(typing.Protocol):
    def fly(self):...



class Duck(BaseModel):
    name:str
    age:int
    def __int__(self,name:str,age:int):
        self.name = name
        self.age = age
    def fly(self):
        print("中国鸭能飞")

import json
import pydantic



class User(pydantic.BaseModel):
    id:str
    name:str
    age:int

json_str :str = '{"id":"u001","name":"张三","age":22}'

user1 = User.model_validate_json(json_str) # json字符串转成实例
user1_dict = json.loads(json_str) # json字符串转成字典
user2 = User.model_validate(user1_dict ) # 字典转换为对应的实例

print(user1)
print(user1_dict)
print(user2)



json_str2 = User.model_dump_json(user1)#user转换为对应的json
json_str3 = json.dumps(user1_dict)#字典转化为对应的json
instance_dict = User.model_dump(user1)#user 实例转化为对应的字典
print(instance_dict)



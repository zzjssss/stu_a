import pydantic
import json

import typing

class User(pydantic.BaseModel):
    id:str
    name:str
    age:int

json_str :str = '{"id":"u001","name":"张三","age":22}'  # 假设是传到后端的json

#json 转化为 dict  print(json_dict)
json_dict = json.loads(json_str)


#dict 转化为对应实例print(user)
user = User.model_validate(json_dict)


#json 转化为 实例 print(user_fromjson)
user_fromjson = User.model_validate_json(json_str)

#实例转化为json
json_str2 = User.model_dump_json(user_fromjson)
#实例转化为dict
dict2 = User.model_dump(user_fromjson)
#dict 转化为json
json_str3 = json.dumps(dict2)
print(json_str3)
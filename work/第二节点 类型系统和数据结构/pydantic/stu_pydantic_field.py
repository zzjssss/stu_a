from typing import Optional,List
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(gt=0, description="用户ID")
    username: str = Field(min_length=2)
    age: Optional[int] = Field(None, ge=0)
    tags: List[str] = Field(default_factory=list)  # noqa
# 原始JSON字符串
json_text = '''
{
    "id": 1001,
    "username": "zhangsan",
    "age": 22,
    "tags": ["student", "dev"]
}
'''

# 1. JSON字符串 解析成模型对象
user = User.model_validate_json(json_text)
print("模型对象：", user)
print("user.username =", user.username)

# 2. 模型对象序列化为 JSON字符串
out_json = user.model_dump_json(indent=2)
print("\n输出JSON：")
print(out_json)

# 3. 模型转 Python dict
data_dict = user.model_dump()
print("\npython dict:", data_dict)
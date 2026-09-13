import typing

USERS: dict[int, dict[str, typing.Any]] = {1: {"name": "张三", "score": 85}}


def find_user(uid: int) -> dict[str, typing.Any] | None:
    return USERS.get(uid)

print(find_user(1))
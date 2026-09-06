users=[
    {"name":"a","city":"广州"},
    {"name":"s","city":"北京"},
    {"name":"d","city":"北京"},
    {"name":"f","city":"北京"},
    {"name":"r","city":"上海"},
    {"name":"t"},

]


def collect_city(users:list[dict]) ->dict:
    result = {}
    for user in users:
        city = user.get("city",None)
        result[city] = result.get(city,0) +1
    return result

print(collect_city(users))
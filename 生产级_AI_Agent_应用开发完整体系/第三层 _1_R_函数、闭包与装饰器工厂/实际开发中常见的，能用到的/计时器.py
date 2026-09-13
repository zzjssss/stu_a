import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        star_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print(f"【计时】{func.__name__} \
        执行耗时：{(end_time-star_time)*1000:.2f} ms")
        return func
    return wrapper

@timer
def query_db():
    time.sleep(0.3)
    return "查询完成"

query_db()
from functools import wraps


def auto_handle_except(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print(f"发现错误- type：{type(e)}   value: {e}")
            return None
    return wrapper

@auto_handle_except
def test():
    print(1/0)
test()
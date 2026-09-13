"""
第 04 节 · 装饰器基础：@ 语法糖的真相
======================================================
学习目标
    1. 能把 @deco 手动展开成等价的普通代码（这是本节唯一必须掌握的技能）
    2. 写出签名通用的 wrapper(*args, **kwargs)
    3. 理解 functools.wraps 不加会丢什么
    4. 掌握多装饰器叠加的"洋葱模型"：注册顺序 vs 执行顺序
    5. 分清两类装饰器：增强型（改行为）与注册型（只登记）
    6. 知道装饰器在"定义时"就执行，不是"调用时"

前置：必须已经吃透 03 节的闭包。装饰器 = 闭包 + 语法糖，没有新魔法。
======================================================
"""

import functools
import time
from collections.abc import Callable
from typing import Any

# 用来演示"装饰器在定义时就执行"
EXECUTION_LOG: list[str] = []


# ############################################################
# 4.1 最简单的装饰器 与 @ 语法糖的等价展开
# ############################################################
def simple_deco(func: Callable[..., Any]) -> Callable[..., Any]:
    """一个装饰器：接收一个函数，返回一个"增强版"函数。"""
    print(f"  [装饰器执行] 正在包装 {func.__name__}")   # 这行在"定义时"就跑

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"    >>> 调用 {func.__name__} 之前")
        result: Any = func(*args, **kwargs)          # 调用原函数
        print(f"    <<< 调用 {func.__name__} 之后")
        return result

    return wrapper


# 写法 A：使用语法糖
@simple_deco
def say_hello(name: str) -> str:
    """打招呼。"""
    return f"hello {name}"


def say_hello_manual(name: str) -> str:
    """打招呼（手动版）。"""
    return f"hello {name}"


# 写法 B：手动展开 —— 与写法 A 完全等价，就这一行！
say_hello_manual = simple_deco(say_hello_manual)


def demo_4_1() -> None:
    print("\n--- 4.1 @ 语法糖的等价展开 ---")
    # 注意：上面两行 print("[装饰器执行]...") 在模块加载时就已经打印过了
    print("  say_hello 现在的类型:", type(say_hello).__name__)
    print("  say_hello.__name__   :", say_hello.__name__)   # wrapper，不是 say_hello！
    print()
    print("  调用 @simple_deco 版本 :", say_hello("A"))
    print("  调用 手动展开版本      :", say_hello_manual("B"))
    print("""
    结论（背下来）：
        @deco
        def f(): ...
    完全等价于
        def f(): ...
        f = deco(f)
    装饰器做的事就一件：把原来的函数名，重新绑定到另一个函数对象上。
""")


# ############################################################
# 4.2 装饰器的执行时机：定义时，不是调用时
# ############################################################
def timing(func: Callable[..., Any]) -> Callable[..., Any]:
    """计时装饰器：统计函数执行耗时（秒），保留 6 位小数输出。"""
    EXECUTION_LOG.append(f"装饰 {func.__name__}")

    @functools.wraps(func)      # 4.3 会讲，先照抄
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start: float = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            # finally 保证即使函数抛异常，耗时也会被记录
            cost: float = time.perf_counter() - start
            print(f"    [timing] {func.__name__} 耗时 {cost:.6f} 秒")

    return wrapper


@timing
def slow_add(a: int, b: int) -> int:
    time.sleep(0.2)
    return a + b


def demo_4_2() -> None:
    print("\n--- 4.2 执行时机 ---")
    print("  模块加载阶段就发生了:", EXECUTION_LOG)
    print("  现在才开始真正调用:")
    print("  slow_add(1, 2) =", slow_add(1, 2))
    print("""
    要点：
      · 装饰器本体（deco 函数里的代码）在 def 语句执行时立即运行一次
      · wrapper 里的代码在每次调用被装饰函数时运行
      · 这就是为什么 Flask 的路由表能在 app.run() 之前就注册完毕
""")


# ############################################################
# 4.3 functools.wraps：不加会丢失原函数的"身份"
# ############################################################
def deco_without_wraps(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)
    return wrapper


def deco_with_wraps(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)      # 把 func 的元信息复制到 wrapper 上
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)
    return wrapper


@deco_without_wraps
def original_a(x: int) -> int:
    """我是 original_a 的文档字符串。"""
    return x


@deco_with_wraps
def original_b(x: int) -> int:
    """我是 original_b 的文档字符串。"""
    return x


def demo_4_3() -> None:
    print("\n--- 4.3 functools.wraps ---")
    for f in (original_a, original_b):
        print(f"  __name__={f.__name__:10s} __doc__={f.__doc__!r:38s} "
              f"__wrapped__={'有' if hasattr(f, '__wrapped__') else '无'}")
    print("""
    不加 wraps 的后果：
      1. __name__ / __doc__ / __module__ / __annotations__ 全变成 wrapper 的
      2. 日志里打出来全是 "wrapper"，排错时根本找不到是哪个函数
      3. 调试器、pytest、Sphinx 文档、inspect.signature 全部失效
      4. 没有 __wrapped__，无法通过它拿回原函数
    规矩：写装饰器，@functools.wraps(func) 是标配，永远别省。
""")


# ############################################################
# 4.4 多装饰器叠加：洋葱模型
# ############################################################
def make_tag(tag: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """造一个打印标记的装饰器，方便观察叠加顺序。"""

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        print(f"  [注册阶段] {tag} 包装 {func.__name__}")

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"    [调用阶段] {tag} 进入")
            result: Any = func(*args, **kwargs)
            print(f"    [调用阶段] {tag} 退出")
            return result

        return wrapper

    return deco


@make_tag("外层A")
@make_tag("中层B")
@make_tag("内层C")
def target() -> str:
    print("      >>> 真正的业务函数 target")
    return "done"


def demo_4_4() -> None:
    print("\n--- 4.4 叠加顺序（洋葱模型） ---")
    print("  现在调用 target():")
    target()
    print("""
    展开等价代码（从下往上包）：
        target = make_tag("外层A")(make_tag("中层B")(make_tag("内层C")(target)))

    两条铁律：
      · 注册（包装）顺序：自下而上，离函数最近的先包
      · 调用（执行）顺序：自上而下进，自下而上出 —— 像穿过洋葱再穿回来
      · 所以：最上面的装饰器"权限最大"，它决定要不要继续往里走
        （这就是权限校验、缓存通常写在最外层的原因）
""")


# ############################################################
# 4.5 注册型装饰器：不改变行为，只把函数登记到表里
# ############################################################
HANDLERS: dict[str, Callable[..., Any]] = {}


def register(name: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """把函数注册进 HANDLERS 字典，原函数原样返回。

    这是"命令模式 / 插件系统 / 路由表"的核心手法。
    """

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        key: str = name or func.__name__
        HANDLERS[key] = func
        return func             # 注意：直接返回原函数，不做任何包装

    return deco


@register("加法")
def add(a: int, b: int) -> int:
    return a + b


@register()
def sub(a: int, b: int) -> int:
    return a - b


@register("乘法")
def mul(a: int, b: int) -> int:
    return a * b


def demo_4_5() -> None:
    print("\n--- 4.5 注册型装饰器 ---")
    print("  注册表内容:", {k: v.__name__ for k, v in HANDLERS.items()})
    print("  sub 没被包装:", sub.__name__)

    # 用名字驱动调用，彻底消灭 if-elif 长链
    for op in ("加法", "sub", "乘法"):
        handler: Callable[..., Any] = HANDLERS[op]
        print(f"    {op:4s}(6, 2) = {handler(6, 2)}")
    print("""
    要点：
      · return func 而不是 return wrapper，函数行为完全不变，零性能损耗
      · 注册表是模块级字典，import 这个模块时所有装饰器自动跑完
      · 新增一种运算只要加一个 @register 函数，不用改任何分发逻辑
        —— 这就是"开闭原则"（对扩展开放，对修改关闭）
""")


# ############################################################
# ★ 实战片段 1：接口耗时统计 + 慢查询告警
# ############################################################
# 场景说明：
#   上线后发现某个接口偶发很慢，需要在不改动任何业务代码的前提下，
#   给关键函数加上耗时统计，超过阈值就打告警。
#   用装饰器可以做到"业务代码一行不动"，这正是 AOP（面向切面编程）的思想。
# ------------------------------------------------------------
def monitor(threshold_ms: float = 100.0) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """性能监控装饰器工厂（下一节详解，这里先看用法）。

    :param threshold_ms: 超过多少毫秒就打 WARN 日志
    """

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start: float = time.perf_counter()
            error: Exception | None = None
            try:
                return func(*args, **kwargs)
            except Exception as e:      # 记录异常但继续抛出，不吞异常
                error = e
                raise
            finally:
                cost_ms: float = (time.perf_counter() - start) * 1000
                level: str = "WARN" if cost_ms > threshold_ms else "INFO"
                status: str = "OK" if error is None else f"ERR({type(error).__name__})"
                print(f"  [{level:4s}] {func.__module__}.{func.__qualname__} "
                      f"{status} {cost_ms:.3f}ms args={args} kwargs={kwargs}")

        return wrapper

    return deco


@monitor(threshold_ms=50.0)
def query_user_list(page: int, size: int = 10) -> list[dict[str, Any]]:
    """模拟一个数据库查询接口。"""
    time.sleep(0.08)
    return [{"id": page * size + i, "name": f"user{i}"} for i in range(size)]


@monitor(threshold_ms=1000.0)
def fast_calc(x: int) -> int:
    return x * x


def practice_monitor() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 1：耗时统计 + 慢查询告警")
    print("=" * 56)
    users = query_user_list(page=2, size=3)
    print("  查到用户数:", len(users))
    print("  fast_calc(9) =", fast_calc(9))

    @monitor(threshold_ms=1.0)
    def will_fail() -> None:
        raise ValueError("模拟业务异常")

    try:
        will_fail()
    except Exception as e:
        print("  异常正常向外抛出:", e)

    print("""
讲解要点：
 1. try / except / finally 三件套是监控装饰器的标准结构：
      try     -> 执行原函数
      except  -> 记录异常后 raise 原样抛出（千万不要吞掉异常！）
      finally -> 无论成功失败都要统计耗时
 2. func.__module__ + func.__qualname__ 能打出 "模块.类.函数" 完整路径，
    日志里定位问题全靠它，所以 functools.wraps 不能省。
 3. 耗时用 time.perf_counter()（高精度、专为计时设计），
    不要用 time.time()（精度低且会被系统改时间影响）。
 4. 阈值做成装饰器参数后，核心接口设 50ms、报表接口设 5000ms，各管各的。
 5. 生产环境把 print 换成 logger.warning / 上报到 Prometheus，逻辑完全一样。
""")


# ############################################################
# ★ 实战片段 2：登录 / 权限校验
# ############################################################
# 场景说明：
#   后台系统里几十个接口都需要"先判断登录、再判断角色"。
#   把校验逻辑写进每个函数会重复几十遍，用装饰器一行搞定。
#   Django 的 @login_required、@permission_required 就是这个东西。
# ------------------------------------------------------------
CURRENT_USER: dict[str, Any] = {"id": 1, "name": "周志杰", "roles": {"user"}}


def login_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """未登录直接拒绝，不进业务函数。"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not CURRENT_USER:
            return {"code": 401, "msg": "未登录，请先登录"}
        return func(*args, **kwargs)

    return wrapper


def role_required(*roles: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """要求当前用户拥有指定角色之一。"""

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            owned: set[str] = CURRENT_USER.get("roles", set())
            if not owned & set(roles):          # 集合交集判空
                return {"code": 403, "msg": f"需要角色 {roles}，当前 {owned or '无'}"}
            return func(*args, **kwargs)

        return wrapper

    return deco


@login_required
@role_required("admin")
def delete_user(user_id: int) -> dict[str, Any]:
    """危险操作：只有管理员能做。"""
    return {"code": 200, "msg": f"已删除用户 {user_id}"}


@login_required
def get_profile() -> dict[str, Any]:
    return {"code": 200, "msg": f"你好, {CURRENT_USER['name']}"}


def practice_auth() -> None:
    # 需要在函数里给模块级变量赋值，所以必须先声明 global
    # （global 语句必须写在函数体开头，否则是 SyntaxError）
    global CURRENT_USER

    print("\n" + "=" * 56)
    print("★ 实战片段 2：登录 / 权限校验")
    print("=" * 56)

    print("  1) 普通用户访问个人信息:", get_profile())
    print("  2) 普通用户尝试删人    :", delete_user(9))

    CURRENT_USER = {"id": 2, "name": "管理员", "roles": {"user", "admin"}}
    print("  3) 管理员尝试删人      :", delete_user(9))

    CURRENT_USER = {}
    print("  4) 未登录访问个人信息  :", get_profile())
    CURRENT_USER = {"id": 1, "name": "周志杰", "roles": {"user"}}

    print("""
讲解要点：
 1. 两个装饰器叠加时，@login_required 写在上面 -> 它先执行。
    顺序反了就会出现"未登录也返回 403 而不是 401"的语义错误。
 2. 校验失败要 return 一个统一格式的响应体，而不是抛异常，
    Web 框架里通常会 raise PermissionDenied 交给全局异常处理器转成 403。
 3. CURRENT_USER 是模块级全局变量，方便演示。真实项目里应该从
    请求上下文（Flask 的 g / request、FastAPI 的 Depends）中取，
    否则多线程下会串号 —— 这是初学者最容易忽略的严重问题。
 4. 装饰器让"业务函数只关心业务"，横切关注点（认证/日志/事务/缓存）
    全部剥离出去，这就是 AOP 的价值。
""")


# ############################################################
# ★ 实战片段 3：Flask 路由注册的最小实现
# ############################################################
ROUTES: dict[str, Callable[..., str]] = {}


def route(path: str, methods: tuple[str, ...] = ("GET",)) \
        -> Callable[[Callable[..., str]], Callable[..., str]]:
    """模仿 Flask 的 @app.route，把 URL 与处理函数绑定起来。"""

    def deco(func: Callable[..., str]) -> Callable[..., str]:
        ROUTES[path] = func
        # 顺便把允许的方法挂到函数对象上，供框架查询
        setattr(func, "methods", methods)
        return func                     # 原函数不变，纯注册

    return deco


@route("/index")
def index() -> str:
    return "<h1>首页</h1>"


@route("/user/<int:uid>", methods=("GET", "POST"))
def user_detail(uid: int) -> str:
    return f"用户详情 id={uid}"


def dispatch(path: str) -> str:
    """模拟框架的请求分发：按 URL 找到处理函数并调用。"""
    handler: Callable[..., str] | None = ROUTES.get(path)
    if handler is None:
        return "404 Not Found"
    return handler()


def practice_flask_route() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 3：Flask 路由注册原理")
    print("=" * 56)
    print("  路由表:", list(ROUTES.keys()))
    for path, fn in ROUTES.items():
        print(f"    {path:20s} -> {fn.__name__:12s} "
              f"methods={getattr(fn, 'methods', ())}")
    print("  访问 /index        :", dispatch("/index"))
    print("  访问 /not/exist    :", dispatch("/not/exist"))
    print("  访问 /user/<int:uid>:", user_detail(1001))
    print("""
讲解要点：
 1. Flask 的 @app.route("/index") 本质就是这里的 route()：
    把 path -> func 存进一个字典（Flask 里叫 url_map），return func 不做包装。
 2. 因为 return 的是原函数，所以 index() 依然可以像普通函数一样直接调用和测试。
 3. app 是一个实例，所以 Flask 的 route 是"方法装饰器工厂"：
       class Flask:
           def route(self, path):        # self 已绑定，所以能写 @app.route(...)
               def deco(func): ...
               return deco
    这解释了为什么必须写 @app.route 而不能写 @route。
 4. 真实框架还会做路径参数解析（<int:uid> -> 正则匹配 + 类型转换）、
    请求方法校验、蓝图分组，但核心机制就是"装饰器 + 注册表"。
""")


# ############################################################
if __name__ == "__main__":
    demo_4_1()
    demo_4_2()
    demo_4_3()
    demo_4_4()
    demo_4_5()
    practice_monitor()
    practice_auth()
    practice_flask_route()
    print("\n[04 节完] 下一节：05_装饰器工厂.py —— 重点与难点")

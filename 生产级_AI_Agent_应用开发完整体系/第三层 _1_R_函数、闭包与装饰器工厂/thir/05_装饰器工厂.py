"""
第 05 节 · 装饰器工厂（带参数的装饰器）—— 重点与难点
======================================================
学习目标
    1. 理解为什么需要"三层嵌套"，能默写出结构
    2. 写出生产可用的 @retry(times=3, delay=0.5, exceptions=(...))
    3. 掌握"带括号 / 不带括号"两种调用形态的兼容写法
    4. 会用类实现装饰器（__init__ + __call__），知道何时该选它
    5. 会用装饰器装饰"类"（单例、批量注册方法）
    6. 掌握 functools 全家桶：lru_cache / partial / singledispatch / cached_property

核心区别（务必分清三层各是谁的参数）
    def deco_factory(配置参数):        # 第1层：工厂，接收"你的配置"
        def deco(func):                # 第2层：真正的装饰器，接收"被装饰的函数"
            def wrapper(*a, **kw):     # 第3层：替身，接收"调用时的实参"
                ...
                return func(*a, **kw)
            return wrapper
        return deco

    @deco_factory(配置参数)   ->   func = deco_factory(配置参数)(func)
======================================================
"""

import functools
import inspect
import threading
import time
from collections.abc import Callable
from typing import Any


# ############################################################
# 5.1 从"写死的装饰器"到"可配置的装饰器工厂"
# ############################################################
def repeat_twice(func: Callable[..., Any]) -> Callable[..., Any]:
    """写死版本：永远执行两次。想改成三次就得改源码。"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        for _ in range(2):
            result: Any = func(*args, **kwargs)
        return result

    return wrapper


def repeat(times: int = 2) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """工厂版本：次数由调用方决定。"""

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result: Any = None
            for i in range(1, times + 1):
                result = func(*args, **kwargs)
                print(f"      第 {i}/{times} 次执行完成")
            return result

        return wrapper

    return deco


@repeat_twice
@repeat(times=3)
def hello(name: str) -> str:
    print(f"      hello {name}")
    return name


def demo_5_1() -> None:
    print("\n--- 5.1 工厂 vs 写死 ---")
    hello("周志杰")
    # 展开：hello = repeat_twice(repeat(times=3)(hello))
    # repeat(times=3) 先执行 -> 返回 deco -> deco(hello) 返回 wrapper
    # repeat_twice 再包装一层 -> 所以整体跑了 3 * 2 = 6 次
    print("""
    数一数输出："hello 周志杰" 出现了 6 次，正好验证了上面的展开过程。
    这就是为什么 @repeat(times=3) 必须带括号：
        repeat(times=3) 的返回值才是真正的装饰器。
""")


# ############################################################
# 5.2 ★ 生产级重试装饰器（最经典的装饰器工厂）
# ############################################################
def retry(times: int = 3,
          delay: float = 0.0,
          backoff: float = 1.0,
          exceptions: tuple[type[BaseException], ...] = (Exception,),
          on_fail: Callable[[Exception, int], None] | None = None
          ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """失败自动重试装饰器工厂。

    :param times:      最多尝试次数（含第一次），必须 >= 1
    :param delay:      每次重试前的等待秒数
    :param backoff:    退避倍数，1.0=固定间隔，2.0=指数退避（1,2,4,8...）
    :param exceptions: 只有这些异常才重试，其他异常立即抛出
    :param on_fail:    每次失败后的回调，用于上报监控 / 打日志
    """
    if times < 1:
        raise ValueError("times 必须 >= 1")

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            wait: float = delay
            last_exc: Exception | None = None

            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:          # 只捕获声明过的异常
                    last_exc = e
                    print(f"      [retry] {func.__name__} 第 {attempt}/{times} 次失败: "
                          f"{type(e).__name__}: {e}")
                    if on_fail is not None:
                        on_fail(e, attempt)
                    if attempt < times and wait > 0:
                        time.sleep(wait)
                        wait *= backoff          # 指数退避
                # 不在 exceptions 里的异常不会被捕获，直接向外抛，符合预期

            # 所有次数都失败，抛出最后一次的异常
            raise RuntimeError(
                f"{func.__name__} 重试 {times} 次仍失败"
            ) from last_exc

        return wrapper

    return deco


ATTEMPT_STATE: dict[str, int] = {"n": 0}


@retry(times=4, delay=0.05, backoff=2.0, exceptions=(ConnectionError,))
def call_third_party_api(order_id: int) -> str:
    """模拟一个不稳定的第三方接口：前 3 次超时，第 4 次成功。"""
    ATTEMPT_STATE["n"] += 1
    if ATTEMPT_STATE["n"] < 4:
        raise ConnectionError(f"请求订单 {order_id} 超时")
    return f"订单 {order_id} 查询成功"


@retry(times=2, exceptions=(ConnectionError,))
def always_fail() -> None:
    raise ConnectionError("服务不可用")


def demo_5_2() -> None:
    print("\n--- 5.2 重试装饰器 ---")
    start = time.perf_counter()
    print("  最终结果:", call_third_party_api(1001))
    print(f"  总耗时(含指数退避 0.05+0.1+0.2): {time.perf_counter() - start:.3f} 秒")

    print("\n  全部失败的情况：")
    try:
        always_fail()
    except Exception as e:
        print(f"  最终抛出: {type(e).__name__}: {e}")
        print(f"  原始异常链: {e.__cause__!r}")

    # 不属于 exceptions 的异常不会重试，直接抛出
    @retry(times=5, exceptions=(ConnectionError,))
    def value_bug() -> None:
        raise ValueError("这是代码 bug，重试没意义")

    try:
        value_bug()
    except Exception as e:
        print(f"\n  非重试异常直接抛出: {type(e).__name__}: {e}")

    print("""
讲解要点：
 1. 一定要限定 exceptions。对所有异常都重试是灾难：
    ValueError/TypeError 属于代码 bug，重试 100 次也一样错，只会拖慢故障发现。
 2. 指数退避 backoff：网络抖动时固定间隔会持续撞墙，
    0.5s -> 1s -> 2s -> 4s 给下游喘息时间，这是所有大厂 SDK 的默认策略。
 3. raise ... from last_exc 保留异常链，日志里能看到"最初的错误"，排障必备。
 4. on_fail 回调让重试逻辑与监控上报解耦（开闭原则）。
 5. 生产环境可直接用第三方库 tenacity，它的 @retry 就是这个东西的加强版；
    但面试和读源码时，你必须能自己写出来。
""")


# ############################################################
# 5.3 兼容"带括号"和"不带括号"两种写法
# ############################################################
# 痛点：@log 和 @log() 都能用，否则使用者忘了写括号就会得到诡异报错
# ------------------------------------------------------------
def logged(func: Callable[..., Any] | None = None, *,
           prefix: str = "LOG") -> Any:
    """既能 @logged 也能 @logged(prefix="SQL") 的兼容写法。

    原理：
      · 写 @logged            -> Python 传进来的是"被装饰的函数"，func 不为 None
      · 写 @logged(prefix=x)  -> 先调用 logged(prefix=x)，func 为 None，
                                 此时必须返回"真正的装饰器"
    """

    def deco(f: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 把实参拼接成可读的字符串；直接写 f"{args}" 会得到 ("x",) 这种带尾逗号的形式
            shown: str = ", ".join(repr(a) for a in args)
            if kwargs:
                shown = f"{shown}, {kwargs}" if shown else str(kwargs)
            print(f"      [{prefix}] 调用 {f.__name__}({shown})")
            return f(*args, **kwargs)

        return wrapper

    if func is None:          # 带括号的用法：@logged() 或 @logged(prefix="SQL")
        return deco
    return deco(func)         # 不带括号的用法：@logged


@logged
def plain_add(a: int, b: int) -> int:
    return a + b


@logged()
def empty_paren_add(a: int, b: int) -> int:
    return a + b


@logged(prefix="SQL")
def query(sql: str) -> list[str]:
    return [sql]


def demo_5_3() -> None:
    print("\n--- 5.3 兼容带/不带括号 ---")
    print("  ", plain_add(1, 2))
    print("  ", empty_paren_add(3, 4))
    print("  ", query("select * from user"))
    print("""
    关键技巧：
      1. 第一个位置参数默认值设为 None，其余配置参数全部写成"仅关键字"（* 之后），
         这样 @logged("SQL") 这种歧义写法根本不可能发生。
      2. if func is None: return deco 是判断"用户有没有写括号"的唯一可靠方式。
      3. 标准库 functools.lru_cache 在 3.8 之后也支持了这种双形态写法。
""")


# ############################################################
# 5.4 用"类"实现装饰器
# ############################################################
class CountCalls:
    """类装饰器：__init__ 接收被装饰函数，__call__ 让实例变成可调用对象。

    什么时候用类实现？
      · 状态很多（计数、缓存、锁、统计指标），闭包变量会写得很乱
      · 需要对外暴露方法（清缓存、读统计、重置状态）
      · 需要继承 / 组合复用
    """

    def __init__(self, func: Callable[..., Any]) -> None:
        functools.update_wrapper(self, func)   # 类版的 wraps，同样不能省
        self.func: Callable[..., Any] = func
        self.count: int = 0
        self.total_cost: float = 0.0
        self._lock = threading.Lock()          # 多线程下计数要加锁

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return self.func(*args, **kwargs)
        finally:
            cost = time.perf_counter() - start
            with self._lock:
                self.count += 1
                self.total_cost += cost

    # 类实现独有的好处：可以定义额外方法
    def stats(self) -> str:
        avg = self.total_cost / self.count if self.count else 0.0
        return f"调用 {self.count} 次, 累计 {self.total_cost:.6f}s, 平均 {avg:.6f}s"

    def reset(self) -> None:
        with self._lock:
            self.count = 0
            self.total_cost = 0.0


@CountCalls
def risky_divide(a: float, b: float) -> float:
    return a / b


def demo_5_4() -> None:
    print("\n--- 5.4 类实现的装饰器 ---")
    print("  类型:", type(risky_divide).__name__, "  名字:", risky_divide.__name__)
    for i in range(1, 4):
        print(f"    {i * 10}/{i} =", risky_divide(i * 10, i))
    print("  统计:", risky_divide.stats())
    risky_divide.reset()
    print("  重置后:", risky_divide.stats())
    print("""
    注意：被类装饰器装饰后，函数名绑定的是"实例"而不是函数对象。
          所以 isinstance(risky_divide, CountCalls) 为 True，
          inspect.signature 依然可用（因为 update_wrapper 复制了 __wrapped__）。
""")


class CountCallsFactory:
    """带参数的类装饰器工厂：__init__ 收配置，__call__ 收函数。

    对比函数式三层结构：
        函数式: factory(config) -> deco(func) -> wrapper(*args)
        类  式: __init__(config) -> __call__(func) -> 实例(*args)  需要两层类
    """

    def __init__(self, tag: str = "TAG") -> None:
        self.tag = tag

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"      <{self.tag}> {func.__name__} 开始")
            try:
                return func(*args, **kwargs)
            finally:
                print(f"      </{self.tag}> {func.__name__} 结束")

        return wrapper


@CountCallsFactory(tag="SERVICE")
def place_order(order_id: int) -> str:
    return f"下单成功 {order_id}"


def demo_5_4b() -> None:
    print("\n--- 5.4b 带参数的类装饰器 ---")
    print("  ", place_order(2024))


# ############################################################
# 5.5 装饰"类"：单例与批量注册
# ############################################################
def singleton(cls: type) -> Callable[..., Any]:
    """单例装饰器：无论 new 多少次，都返回同一个实例。"""
    instances: dict[type, Any] = {}
    lock = threading.Lock()

    @functools.wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        with lock:                       # 双重检查加锁，线程安全
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Config:
    """全局配置类，只应该存在一份。"""

    def __init__(self, env: str = "dev") -> None:
        self.env: str = env
        print(f"      [Config] 初始化，env={env}")


def demo_5_5() -> None:
    print("\n--- 5.5 装饰类：单例 ---")
    a = Config("prod")
    b = Config("test")        # 注意：第二次不会再初始化，env 依然是 prod
    print("  a is b :", a is b)
    print("  a.env  :", a.env)
    print("""
    讨论：装饰器单例写起来爽，但它把 Config 变成了函数，
          静态检查工具会认为 Config 不再是类（无法继承、无类型提示）。
          正式项目更推荐用模块级单例（Python 的模块天然就是单例）：
              config = Config()   # 放在模块底部，别处 import config
    """)


# ############################################################
# 5.6 functools 全家桶：官方已经帮你写好的"装饰器工厂"
# ############################################################
@functools.lru_cache(maxsize=128)
def fib_cached(n: int) -> int:
    """官方缓存装饰器，比 03 节手写的更强（有容量上限 + 线程安全 + 统计）。"""
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


def power(base: float, exp: float) -> float:
    return base ** exp


@functools.singledispatch
def describe(value: Any) -> str:
    """singledispatch：按第一个参数的类型自动分派到不同实现。

    被 @functools.singledispatch 装饰后，describe 不再是普通函数，
    而是一个 GenericFunction 对象，所以才拥有 .register / .dispatch 方法。
    """
    return f"未知类型 {type(value).__name__}: {value}"


@describe.register
def _(value: int) -> str:
    return f"整数: {value}"


@describe.register
def _(value: list) -> str:
    return f"列表，长度 {len(value)}"


class User:
    def __init__(self, name: str) -> None:
        self.name = name


@describe.register(User)
def _(value: User) -> str:
    return f"用户对象: {value.name}"


def demo_5_6() -> None:
    print("\n--- 5.6 functools 全家桶 ---")
    print("  lru_cache  : fib(80) =", fib_cached(80))
    print("  缓存统计   :", fib_cached.cache_info())

    # partial：固定部分参数，生成新函数（闭包工厂的官方替代品）
    square: Callable[[float], float] = functools.partial(power, exp=2)
    cube: Callable[[float], float] = functools.partial(power, exp=3)
    print(f"  partial    : square(3)={square(3):.3f}, cube(3)={cube(3):.3f}")

    print("  singledispatch:")
    for v in (10, [1, 2, 3], User("小明"), 3.14):
        print(f"      {describe(v)}")

    print("""
    选型建议：
      · 只是缓存纯函数结果        -> @lru_cache / @cache，别自己写
      · 只是固定几个参数          -> functools.partial
      · 按类型分派不同实现        -> @singledispatch，替代 isinstance 长链
      · 需要复杂状态/多方法/可配置 -> 自己写装饰器工厂或类装饰器
      · 只是打日志/校验/限流/重试  -> 自己写，因为业务语义无法被官方覆盖
""")


# ############################################################
# ★ 实战片段 1：带脱敏的日志装饰器（后台系统必备）
# ############################################################
SENSITIVE_KEYS: frozenset[str] = frozenset(
    {"password", "pwd", "token", "secret", "id_card", "phone", "bank_card"}
)


def mask(value: Any) -> str:
    """把敏感值脱敏成 ***，保留头尾便于人工核对。"""
    s = str(value)
    if len(s) <= 4:
        return "***"
    return f"{s[:2]}***{s[-2:]}"


def render_args(func: Callable[..., Any], args: tuple[Any, ...],
                kwargs: dict[str, Any], mask_args: bool) -> str:
    """把实参绑定到形参名上，再按"形参名"决定是否脱敏。

    为什么不直接按下标脱敏？
      因为 f("zhou", "pwd123") 里哪个位置是密码完全取决于函数定义，
      用 inspect.signature 绑定后，才能稳定地按参数名 password/phone 来判断。
      这也是 functools.wraps 必须写的原因之一：不写的话
      inspect.signature 拿到的是 wrapper(*args, **kwargs)，根本绑不上。
    """
    sig = inspect.signature(func)
    try:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()          # 补齐默认值，日志里能看到完整参数
    except TypeError as e:
        return f"<参数绑定失败: {e}>"

    parts: list[str] = []
    for name, value in bound.arguments.items():
        if mask_args and name.lower() in SENSITIVE_KEYS:
            parts.append(f"{name}={mask(value)}")
        else:
            parts.append(f"{name}={value!r}")
    return ", ".join(parts)


def audit_log(module: str = "app", level: str = "INFO",
              mask_args: bool = True) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """审计日志装饰器工厂。

    :param module:    业务模块名，方便日志检索
    :param level:     日志级别
    :param mask_args: 是否对敏感参数脱敏（生产环境必须开）
    """

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            trace_id: str = f"{int(time.time() * 1000) % 100000:05d}"

            # 1) 组装可打印的参数：按"形参名"判断是否敏感，而不是按位置
            args_text: str = render_args(func, args, kwargs, mask_args)

            start = time.perf_counter()
            print(f"  [{level}][{module}][{trace_id}] --> {func.__name__}({args_text})")
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                cost_ms = (time.perf_counter() - start) * 1000
                print(f"  [ERROR][{module}][{trace_id}] <-- {func.__name__} "
                      f"失败 {cost_ms:.3f}ms {type(e).__name__}: {e}")
                raise
            cost_ms = (time.perf_counter() - start) * 1000
            print(f"  [{level}][{module}][{trace_id}] <-- {func.__name__} "
                  f"成功 {cost_ms:.3f}ms 返回={result!r}")
            return result

        return wrapper

    return deco


@audit_log(module="user.service", mask_args=True)
def register(username: str, password: str, phone: str) -> dict[str, Any]:
    """注册接口：密码和手机号必须脱敏后才能进日志。"""
    if len(password) < 6:
        raise ValueError("密码长度不足 6 位")
    return {"id": 10086, "username": username}


def practice_audit_log() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 1：带脱敏的审计日志装饰器")
    print("=" * 56)
    register("zhouzhijie", "abc123456", phone="13800138000")
    try:
        register("test", "123", phone="13900139000")
    except Exception as e:
        print("  业务异常已向外抛出:", e)

    print("""
讲解要点：
 1. trace_id 把一次调用的"入参日志"和"出参日志"串起来，
    高并发下靠它才能从几万行日志里捞出一次完整请求。
    真实项目里 trace_id 由网关生成并通过上下文传递（contextvars）。
 2. 脱敏是合规红线：密码、手机号、身份证、银行卡绝不能明文落盘。
    用 SENSITIVE_KEYS 白名单集中管理，新增字段只改一处；
    用 inspect.signature 按"形参名"脱敏，比按"参数位置"可靠得多。
 3. 成功/失败两条路径都要打日志，且失败分支必须 raise，不能吞异常。
 4. 日志装饰器 + 监控装饰器 + 权限装饰器可以叠加使用，各司其职：
        @audit_log(...)
        @monitor(threshold_ms=200)
        @login_required
        def api(): ...
""")


# ############################################################
# ★ 实战片段 2：带过期时间的缓存（TTL Cache）
# ############################################################
def ttl_cache(seconds: float = 60.0,
              maxsize: int = 256) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """缓存装饰器工厂：结果缓存 seconds 秒，超时后重新计算。

    适用场景：汇率、商品分类树、权限菜单等"变化不频繁但查询很贵"的数据。
    """

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        store: dict[Any, tuple[float, Any]] = {}     # key -> (过期时间戳, 值)
        hits: list[int] = [0]
        miss: list[int] = [0]
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key: tuple[Any, ...] = (args, tuple(sorted(kwargs.items())))
            now = time.monotonic()

            with lock:
                item = store.get(key)
                if item is not None and item[0] > now:
                    hits[0] += 1
                    return item[1]

                miss[0] += 1
                value = func(*args, **kwargs)
                # 超出容量就淘汰最早过期的那一条（简化版 LRU）
                if len(store) >= maxsize:
                    oldest = min(store, key=lambda k: store[k][0])
                    del store[oldest]
                store[key] = (now + seconds, value)
                return value

        def cache_clear() -> None:
            """暴露给运维接口：改了配置后立刻让缓存失效。"""
            with lock:
                store.clear()

        def cache_info() -> str:
            total = hits[0] + miss[0]
            rate = hits[0] / total * 100 if total else 0.0
            return f"size={len(store)} hits={hits[0]} miss={miss[0]} 命中率={rate:.2f}%"

        setattr(wrapper, "cache_clear", cache_clear)
        setattr(wrapper, "cache_info", cache_info)
        return wrapper

    return deco


@ttl_cache(seconds=1.0)
def get_exchange_rate(currency: str) -> float:
    """模拟一次很慢的第三方汇率查询。"""
    print(f"      [真实请求] 查询 {currency} 汇率 ...")
    time.sleep(0.3)
    rates = {"USD": 7.12, "EUR": 7.85, "JPY": 0.048}
    return rates.get(currency.upper(), 1.0)


def practice_ttl_cache() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 2：TTL 缓存装饰器")
    print("=" * 56)
    start = time.perf_counter()
    for i in range(3):
        rate = get_exchange_rate("usd")     # 注意大小写不同 -> key 不同！
        print(f"    第{i + 1}次 USD 汇率={rate:.4f} 累计耗时={time.perf_counter() - start:.3f}s")
    get_exchange_rate("USD")
    print("    缓存状态:", getattr(get_exchange_rate, "cache_info")())

    print("    等待 1.1 秒让缓存过期 ...")
    time.sleep(1.1)
    get_exchange_rate("USD")                # 会重新发起真实请求
    print("    缓存状态:", getattr(get_exchange_rate, "cache_info")())

    getattr(get_exchange_rate, "cache_clear")()
    print("    手动清空后:", getattr(get_exchange_rate, "cache_info")())

    print("""
讲解要点：
 1. 缓存 key 必须包含全部参数：get_exchange_rate("usd") 和 ("USD")
    是两个不同的 key，会各查一次。生产代码里应先规范化参数（统一大写）再进缓存。
 2. 存"过期时间戳"而不是"存入时间"，判断时只需一次比较，简单高效。
 3. time.monotonic() 计时不受系统时间跳变影响，缓存过期判断必须用它。
 4. 加锁保证多线程安全；不加锁会出现"缓存击穿"（多个线程同时穿透去查库）。
 5. 一定要暴露 cache_clear()：运营改了数据后能立刻生效，
    否则会出现"改了后台但前台还是旧数据"的经典线上事故。
 6. maxsize 淘汰是必须的，否则缓存无限增长 = 内存泄漏。
    真要上生产，直接用 cachetools.TTLCache 或 Redis。
""")


# ############################################################
# ★ 实战片段 3：幂等 / 防重复提交锁
# ############################################################
def idempotent(window: float = 2.0,
               key_func: Callable[..., str] | None = None,
               message: str = "操作过于频繁，请勿重复提交"
               ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """防重复提交装饰器工厂。

    :param window:   同一个 key 在多少秒内只允许执行一次
    :param key_func: 自定义 key 生成函数，默认用"函数名 + 全部参数"
    :param message:  被拦截时返回的提示信息
    """

    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        last_seen: dict[str, float] = {}
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if key_func is not None:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__qualname__}:{args}:{sorted(kwargs.items())}"
            now = time.monotonic()

            with lock:
                prev = last_seen.get(key)
                if prev is not None and now - prev < window:
                    remain = window - (now - prev)
                    print(f"      [拦截] 重复提交，还需等待 {remain:.2f}s")
                    return {"code": 429, "msg": message}
                last_seen[key] = now
                # 顺手清理过期 key，防止字典无限膨胀
                for k in [k for k, t in last_seen.items() if now - t >= window]:
                    del last_seen[k]

            return func(*args, **kwargs)

        return wrapper

    return deco


@idempotent(window=1.5, key_func=lambda user_id, amount: f"pay:{user_id}")
def create_payment(user_id: int, amount: float) -> dict[str, Any]:
    """支付下单：同一用户 1.5 秒内只允许提交一次，防止重复扣款。"""
    return {"code": 200, "msg": "支付单已创建", "amount": f"{amount:.2f}"}


def practice_idempotent() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 3：防重复提交 / 幂等锁")
    print("=" * 56)
    print("  第1次提交:", create_payment(1, 99.90))
    print("  第2次提交(手抖双击):", create_payment(1, 99.90))
    print("  换个用户提交:", create_payment(2, 50.00))
    time.sleep(1.6)
    print("  1.6秒后再提交:", create_payment(1, 99.90))

    print("""
讲解要点：
 1. key_func 让"幂等维度"可配置：支付按用户、领券按用户+活动、
    下单按订单号。写成参数后同一个装饰器能复用到所有接口。
 2. 这是"业务层防抖"，前端按钮置灰只是体验优化，
    真正的资金安全必须在服务端做幂等（还要配合数据库唯一索引/分布式锁）。
 3. 拦截时返回业务错误码而不是抛异常，前端能直接弹出提示语。
 4. 清理过期 key 那段代码很关键：字典只增不减就是内存泄漏，
    线上跑几个月会 OOM。生产环境这类状态放 Redis 并设置 EXPIRE。
 5. 用 threading.Lock 保证"检查 + 写入"是原子操作，
    否则并发下两个线程都判断为"没提交过"，双双放行。
""")


# ############################################################
if __name__ == "__main__":
    demo_5_1()
    demo_5_2()
    demo_5_3()
    demo_5_4()
    demo_5_4b()
    demo_5_5()
    demo_5_6()
    practice_audit_log()
    practice_ttl_cache()
    practice_idempotent()
    print("\n[05 节完] 下一节：06_综合实战_迷你Web框架.py")

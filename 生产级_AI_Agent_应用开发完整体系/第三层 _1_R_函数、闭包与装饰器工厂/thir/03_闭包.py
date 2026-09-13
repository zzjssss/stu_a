"""
第 03 节 · 闭包（Closure）—— 本套课程的分水岭
======================================================
学习目标
    1. 说清闭包成立的三个条件，并能一眼识别闭包
    2. 会用 __closure__ / cell_contents 查看"被关起来的变量"
    3. 理解 nonlocal 为什么是必需的
    4. 掌握两大经典陷阱：循环延迟绑定、外层变量共享
    5. 明白"闭包 = 没有 self 的轻量对象"，会用它做工厂 / 缓存 / 限流
    6. 为下一节装饰器做好 100% 的准备（装饰器就是闭包的标准应用）

一句话定义
    闭包 = 内层函数 + 它引用的外层函数的局部变量。
    外层函数已经返回结束了，但那些局部变量被内层函数"打包带走"，
    活得比外层函数更久 —— 这就是闭包最神奇的地方。
======================================================
"""

import time
from collections.abc import Callable
from typing import Any


# ############################################################
# 3.1 闭包成立的三个条件
# ############################################################
# 条件 1：函数嵌套（def 里面还有 def）
# 条件 2：内层函数引用了外层函数的局部变量（这个变量叫"自由变量"）
# 条件 3：外层函数把内层函数 return 出去
def make_greeter(prefix: str) -> Callable[[str], str]:
    """工厂函数：根据前缀生产一个专属的问候函数。"""

    def greeter(name: str) -> str:
        # prefix 不是 greeter 的局部变量，也不是全局变量，
        # 它是"外层函数的局部变量" —— 即自由变量(free variable)
        return f"{prefix}, {name}!"

    return greeter      # 返回函数对象本身，注意没有括号


def demo_3_1() -> None:
    print("\n--- 3.1 闭包的三个条件 ---")
    hi = make_greeter("你好")
    hello = make_greeter("Hello")

    # make_greeter 早就执行完返回了，但 prefix 依然活着，而且是"各自一份"
    print(hi("周志杰"))       # 你好, 周志杰!
    print(hello("Zhou"))      # Hello, Zhou!

    # 每次调用工厂都会创建一套全新的自由变量，互不干扰
    print("hi 捕获的变量   :", hi.__code__.co_freevars)     # ('prefix',)
    print("hi 的 prefix     :", hi.__closure__[0].cell_contents)
    print("hello 的 prefix  :", hello.__closure__[0].cell_contents)

    # 对比：不是闭包的情况
    def outer_not_closure() -> Callable[[], int]:
        def inner() -> int:
            return 1        # 没有引用任何外层局部变量
        return inner

    print("没有自由变量 -> __closure__ 为 None:", outer_not_closure().__closure__)


# ############################################################
# 3.2 用 nonlocal 修改被捕获的变量：闭包 = 带状态的函数
# ############################################################
def make_counter_bad() -> Callable[[], int]:
    """错误示范：直接给自由变量赋值会报 UnboundLocalError。"""

    def counter() -> int:
        # count += 1
        # 报错原因：函数内出现赋值 -> Python 认定 count 是"局部变量"
        #           但它又不属于本函数 -> 需要 nonlocal 明确指认
        return 0

    return counter


def make_counter(step: int = 1) -> Callable[[], int]:
    """正确示范：用 nonlocal 声明"我要改的是外层那个 count"。"""
    count: int = 0

    def counter() -> int:
        nonlocal count          # 关键！指向 Enclosing 作用域的 count
        count += step
        return count

    return counter


def make_counter_mutable(step: int = 1) -> Callable[[], int]:
    """技巧：把状态放进可变容器（list/dict），就不需要 nonlocal。

    因为 list.append 是"调用方法"而不是"重新绑定名字"，
    Python 不会把它当赋值，所以能直接读到外层的 state。
    这是 Python 3 之前（没有 nonlocal）的标准写法。
    """
    state: list[int] = [0]

    def counter() -> int:
        state[0] += step
        return state[0]

    return counter


def demo_3_2() -> None:
    print("\n--- 3.2 nonlocal：让闭包拥有状态 ---")
    c1 = make_counter()
    c2 = make_counter(step=10)

    print("c1:", c1(), c1(), c1())    # 1 2 3  —— 状态被记住了
    print("c2:", c2(), c2())          # 10 20  —— 独立的另一份状态
    print("c1 再来一次:", c1())        # 4

    m = make_counter_mutable()
    print("可变容器版:", m(), m(), m())

    make_counter_bad()()  # 只是为了跑通，实际不做事
    print("""
    核心认知：
      闭包让"状态"和"操作状态的函数"绑在一起，
      这正是面向对象里"属性 + 方法"干的事。
      所以说：闭包是穷人的对象，对象是穷人的闭包。
    """)


# ############################################################
# 3.3 陷阱一：循环里创建闭包 —— 延迟绑定（late binding）
# ############################################################
def demo_3_3() -> None:
    print("\n--- 3.3 陷阱：循环延迟绑定 ---")

    # 期望 [0, 1, 2]，实际得到 [2, 2, 2]
    funcs_bad: list[Callable[[], int]] = []
    for i in range(3):
        def f_bad() -> int:
            return i          # 闭包捕获的是"变量 i 本身"，不是"当时的值"
        funcs_bad.append(f_bad)
    print("错误结果:", [f() for f in funcs_bad])
    print("原因：循环结束时 i == 2，三个函数共享同一个 i 的 cell")

    # 修复方式 1（最常用）：用默认参数在"定义时"就把值固定下来
    funcs_fix1: list[Callable[[], int]] = []
    for i in range(3):
        def f_fix1(i: int = i) -> int:    # 右边的 i 是循环变量，左边是形参
            return i
        funcs_fix1.append(f_fix1)
    print("修复1 (默认参数):", [f() for f in funcs_fix1])

    # 修复方式 2（更优雅）：再套一层工厂函数，让每轮都有自己的作用域
    def factory(n: int) -> Callable[[], int]:
        def inner() -> int:
            return n
        return inner

    funcs_fix2 = [factory(i) for i in range(3)]
    print("修复2 (工厂函数):", [f() for f in funcs_fix2])

    # 同样的坑在 lambda 里更常见：
    lambdas_bad = [lambda: i for i in range(3)]
    lambdas_fix = [lambda i=i: i for i in range(3)]
    print("lambda 错误:", [f() for f in lambdas_bad])
    print("lambda 修复:", [f() for f in lambdas_fix])


# ############################################################
# 3.4 陷阱二：闭包变量是"共享"的，不是"快照"
# ############################################################
def demo_3_4() -> None:
    print("\n--- 3.4 陷阱：共享而非快照 ---")
    config: dict[str, Any] = {"timeout": 3}

    def show() -> None:
        print("  当前 timeout =", config["timeout"])

    show()                       # 3
    config["timeout"] = 30       # 外层变量变了
    show()                       # 30  <-- 闭包看到的是"实时值"

    # 这在真实项目里可能是 bug 也可能是特性：
    #   · 想要实时值（如热更新配置）-> 正是我们要的
    #   · 想要快照值（如任务创建时的参数）-> 必须在创建时深拷贝
    snapshot = dict(config)      # 手动做一份快照

    def show_snapshot() -> None:
        print("  快照 timeout =", snapshot["timeout"])

    config["timeout"] = 999
    show()                       # 999
    show_snapshot()              # 30  仍然是当时的值

    # 附带一个内存注意点：
    # 闭包持有外层对象引用 -> 只要闭包活着，那些对象就不会被 GC 回收。
    # 大数据 + 长生命周期闭包 = 内存泄漏，需要时记得手动 del 或置 None。


# ############################################################
# 3.5 闭包的调用链与生命周期
# ############################################################
def demo_3_5() -> None:
    print("\n--- 3.5 多层嵌套与 cell 数量 ---")

    def level1(a: int) -> Callable[[], Any]:
        def level2(b: int) -> Callable[[], tuple[int, int]]:
            def level3() -> tuple[int, int]:
                return a, b        # 同时捕获了 a 和 b
            return level3
        return level2(20)          # b 在这里被固定

    f3 = level1(10)
    print("level3 捕获的自由变量:", f3.__code__.co_freevars)   # ('a', 'b')
    print("cell 内容:", [c.cell_contents for c in f3.__closure__])
    print("调用结果:", f3())
    print("""
    注意：外层的局部变量 a 被"穿透"传递到最内层，
          中间层没有引用它，但它依然存在于最内层的 __closure__ 里。
    """)


# ############################################################
# ★ 实战片段 1：接口限流器（Rate Limiter）
# ############################################################
# 场景说明：
#   短信验证码、支付回调、第三方 API 都有"每分钟最多 N 次"的限制。
#   单机场景下不需要上 Redis，用闭包保存"时间窗口内的调用记录"就够了。
#   这段代码在爬虫、秒杀、防刷接口里非常常见。
# ------------------------------------------------------------
def make_rate_limiter(max_calls: int, period: float) -> Callable[[], bool]:
    """创建一个限流器。

    :param max_calls: 时间窗口内允许的最大调用次数
    :param period:    时间窗口长度（秒）
    :return: allow() 函数，允许调用返回 True，被限流返回 False
    """
    timestamps: list[float] = []      # 自由变量：保存最近的调用时间戳

    def allow() -> bool:
        now: float = time.monotonic()          # monotonic 不受系统时间调整影响
        # 1) 把窗口之外的旧记录清掉
        while timestamps and now - timestamps[0] >= period:
            timestamps.pop(0)
        # 2) 判断窗口内是否还有名额
        if len(timestamps) < max_calls:
            timestamps.append(now)
            return True
        return False

    return allow


def practice_rate_limiter() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 1：接口限流器")
    print("=" * 56)
    # 1 秒内最多 3 次
    limiter = make_rate_limiter(max_calls=3, period=1.0)

    for i in range(1, 7):
        ok: bool = limiter()
        print(f"  第{i}次请求 -> {'放行' if ok else '限流(429 Too Many Requests)'}")

    print("  等待 1 秒让窗口过期 ...")
    time.sleep(1.05)
    print(f"  第7次请求 -> {'放行' if limiter() else '限流'}")

    print("""
讲解要点：
 1. timestamps 列表被 allow() 捕获，函数返回后依然存活，
    这就是"闭包保存状态"在真实项目里的典型用途。
 2. 用 list.append / pop 修改容器内容，不是重新赋值名字，所以不需要 nonlocal。
 3. time.monotonic() 比 time.time() 更适合计时：前者单调递增，不受改系统时间影响。
 4. 工厂参数 max_calls / period 让同一个限流器模板能服务不同接口：
       sms_limiter   = make_rate_limiter(1, 60)   # 短信 1 分钟 1 条
       api_limiter   = make_rate_limiter(100, 1)  # 接口 1 秒 100 次
    这就是"闭包做工厂"的价值：配置与逻辑一次绑定，之后调用无需再传参。
 5. 局限：闭包状态只存在于当前进程内存中，多进程/多机器部署要换 Redis。
""")


# ############################################################
# ★ 实战片段 2：手写记忆化缓存（memoize）
# ############################################################
# 场景说明：
#   递归计算（斐波那契、爬楼梯）、 expensive 的第三方查询、
#   配置解析，都可以用"算过就存起来"的方式提速几十倍。
#   这就是 functools.lru_cache 的简化原理。
# ------------------------------------------------------------
def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """给任意函数加一个字典缓存（装饰器的雏形，下一节正式讲）。"""
    cache: dict[Any, Any] = {}        # 自由变量：跨调用共享的缓存表

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 把参数做成可哈希的 key。dict 不能当 key，所以排序后转元组
        key: tuple[Any, ...] = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            print(f"    [cache MISS] {key} -> 真正执行计算")
            cache[key] = func(*args, **kwargs)
        else:
            print(f"    [cache HIT ] {key} -> 直接返回")
        return cache[key]

    # 把缓存暴露出去，方便外部查看/清理。
    # 等价于 wrapper.cache = cache；用 setattr 是为了不触发类型检查告警
    setattr(wrapper, "cache", cache)
    return wrapper


@memoize
def fib(n: int) -> int:
    """斐波那契：不加缓存是 O(2^n)，加了缓存是 O(n)。"""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def practice_memoize() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 2：手写记忆化缓存")
    print("=" * 56)
    print("  fib(5) 的计算过程：")
    print("  结果:", fib(5))
    print("  再算一次 fib(5)：", fib(5))
    # 取出刚才挂在函数对象上的缓存字典（等价于 fib.cache）
    fib_cache: dict[Any, Any] = getattr(fib, "cache", {})
    print("  缓存内容:", fib_cache)
    print("  耗时对比：")
    start = time.perf_counter()
    fib(30)
    print(f"    fib(30) 用时 {time.perf_counter() - start:.6f} 秒（几乎瞬时）")
    print("""
讲解要点：
 1. cache 字典被 wrapper 闭包捕获，因此"函数调用的历史"得以跨调用保存。
 2. key 必须可哈希：位置参数直接放元组，关键字参数要 sorted 后转元组，
    否则 f(a=1, b=2) 和 f(b=2, a=1) 会被当成两次不同的调用。
 3. setattr(wrapper, "cache", cache) 是给函数对象挂属性，
    外部可以 getattr(fib, "cache").clear() 来清缓存 —— 生产代码里必须有这个能力。
 4. 生产环境直接用 @functools.lru_cache(maxsize=1024)，
    它多了容量上限、线程安全和 cache_info() 统计。手写是为了理解原理。
 5. 注意：被缓存函数的参数必须可哈希（list/dict 作为参数会 TypeError）。
""")


# ############################################################
# ★ 实战片段 3：配置化工厂（日志 / 数据库连接）
# ############################################################
def make_logger(module: str, level: str = "INFO") -> Callable[..., None]:
    """生产一个绑定了模块名和级别的日志函数。

    项目里每个模块开头都有一句 logger = get_logger(__name__)，
    之后写日志就不用每次重复传模块名 —— 靠的就是闭包。
    """
    LEVELS: dict[str, int] = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
    threshold: int = LEVELS.get(level.upper(), 20)

    def log(msg: str, msg_level: str = "INFO") -> None:
        if LEVELS.get(msg_level.upper(), 20) >= threshold:
            stamp: str = time.strftime("%H:%M:%S")
            print(f"{stamp} [{msg_level:5s}] [{module}] {msg}")

    return log


def make_connection_factory(dsn: str, pool_size: int = 5) -> Callable[[], str]:
    """模拟"数据库连接工厂"：把连接串和池大小固定在闭包里。"""
    created: list[str] = []

    def get_conn() -> str:
        if len(created) >= pool_size:
            raise RuntimeError(f"连接池已满({pool_size})，请释放后再试")
        conn_id = f"conn-{len(created) + 1}"
        created.append(conn_id)
        return f"<{conn_id} @ {dsn}>"

    # 等价于 get_conn.created = created，暴露出来供监控查看
    setattr(get_conn, "created", created)
    return get_conn


def practice_factory() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 3：配置化工厂")
    print("=" * 56)
    log_order = make_logger("order.service", "DEBUG")
    log_pay = make_logger("pay.gateway", "WARN")

    log_order("订单创建成功 id=1001")
    log_order("查询订单详情", "DEBUG")
    log_pay("支付渠道初始化完成")            # INFO < WARN，不输出
    log_pay("支付渠道超时，正在重试", "WARN")

    print()
    conn = make_connection_factory("mysql://root@localhost:3306/shop", pool_size=2)
    print(conn())
    print(conn())
    try:
        conn()
    except Exception as e:
        print(f"捕获异常: {type(e).__name__}: {e}")
    created_conns: list[str] = getattr(conn, "created", [])
    print("已创建连接:", created_conns)

    print("""
讲解要点：
 1. 工厂函数把"配置"和"行为"一次性绑定：
       log_pay 只打 WARN 以上，log_order 打 DEBUG 以上，
       调用方写 log_pay("xxx") 时完全不用关心阈值。
 2. 这类"预配置好的可调用对象"就是 functools.partial 的用武之地，
    partial(make_logger, level='WARN') 与闭包工厂效果一致，
    但闭包能写更复杂的初始化逻辑（如上面的 LEVELS 映射表、连接池校验）。
 3. created 列表 = 连接池的真实状态，被闭包持有，进程内全局唯一。
 4. 给函数对象挂属性（setattr(get_conn, 'created', created)）是一种轻量"实例变量"，
    适合监控、调试；但正式代码更建议用类来实现连接池。
""")


# ############################################################
if __name__ == "__main__":
    demo_3_1()
    demo_3_2()
    demo_3_3()
    demo_3_4()
    demo_3_5()
    practice_rate_limiter()
    practice_memoize()
    practice_factory()
    print("\n[03 节完] 你已经掌握了装饰器的全部原理，下一节：04_装饰器基础.py")

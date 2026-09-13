"""
第 02 节 · 作用域 LEGB 与"函数是一等公民"
======================================================
学习目标
    1. 背下并能解释 LEGB 名字查找规则
    2. 分清 global 与 nonlocal 的适用场景
    3. 会读函数对象的内部属性（默认值、自由变量都藏在这里）
    4. 掌握 lambda 的正确用法与它的边界
    5. 熟练使用 map / filter / sorted(key=) / any / all / reduce
       —— 这是写出"Pythonic"数据处理代码的关键，也是装饰器的前置技能
======================================================
"""

import re
from collections import Counter
from functools import reduce
from typing import Any, Callable

# 模块级变量：它属于 G（全局作用域）
COUNT: int = 0
TAX_RATE: float = 0.06


# ############################################################
# 2.1 LEGB：Python 查找一个名字的四层顺序
# ############################################################
# L (Local)     当前函数内部
# E (Enclosing) 外层嵌套函数（下一节闭包的主角）
# G (Global)    模块顶层
# B (Built-in)  内置命名空间（len / print / list ...）
# 查找方向：L -> E -> G -> B，找到即停；都没找到就 NameError
NAME: str = "全局NAME"


def demo_1_1() -> None:
    print("\n--- 2.1 LEGB 查找规则 ---")
    NAME: str = "局部NAME"      # L：局部变量遮蔽(shadow)了全局同名变量
    print("局部:", NAME)         # 局部NAME
    print("全局:", globals()["NAME"])
    print("内置:", len("abc"))   # B：len 在内置命名空间里找到

    # 只读全局变量不需要声明；一旦要"赋值"就必须先 global，
    # 否则 Python 会认为你在创建一个新的局部变量
    print("函数里读全局 TAX_RATE =", TAX_RATE)


def demo_1_2() -> None:
    """global 的正确用法（以及为什么项目里尽量少用）。"""
    print("\n--- 2.2 global ---")
    global COUNT          # 声明：下面的 COUNT 指的是模块级的那个
    COUNT += 1
    print("修改后的全局 COUNT =", COUNT)

    # 反面教材：忘了写 global
    def wrong() -> None:
        # COUNT = COUNT + 1  # 取消注释会报 UnboundLocalError
        # 原因：函数内出现对 COUNT 的赋值 -> Python 判定 COUNT 是局部变量
        #       于是右边的 COUNT 在"局部"里还没被赋值就被读取
        pass

    wrong()
    print("""
    经验：global 会让函数产生"看不见的副作用"，测试和复用都困难。
          真实项目里更推荐：把状态作为参数传入 / 用返回值传出，
          或者把状态封装成类的属性、闭包的自由变量（下一节）。
    """)


# ############################################################
# 2.3 函数对象的内部属性：不要猜，打印出来看
# ############################################################
def inspect_func(f: Callable[..., Any], label: str = "") -> None:
    """把一个函数对象的内部信息打印出来，用于学习和调试。"""
    print(f"===== {label or f.__name__} =====")
    print("  __name__        :", f.__name__)
    print("  __qualname__    :", f.__qualname__)
    print("  __defaults__    :", f.__defaults__)       # 位置参数的默认值元组
    print("  __kwdefaults__  :", f.__kwdefaults__)     # 仅关键字参数的默认值字典
    print("  __annotations__ :", f.__annotations__)
    print("  __code__.co_varnames :", f.__code__.co_varnames)   # 局部变量名
    print("  __code__.co_freevars :", f.__code__.co_freevars)   # 自由变量名（闭包用）
    print("  __closure__     :", f.__closure__)        # 捕获到的 cell 对象


def sample(a: int, b: int = 10, *args: float, flag: bool = True, **kw: Any) -> str:
    """用于被检查的样例函数。"""
    return f"{a}-{b}-{args}-{flag}-{kw}"


def demo_2_3() -> None:
    print("\n--- 2.3 函数对象的内部属性 ---")
    inspect_func(sample, "sample")
    # 关键结论：
    #  __defaults__    -> 只装"位置参数"的默认值 (10,)
    #  __kwdefaults__  -> 只装"* 之后仅关键字参数"的默认值 {'flag': True}
    #  这也再次证明：默认值在 def 执行的那一刻就固定下来了（上一节陷阱的原因）


# ############################################################
# 2.4 lambda：匿名的单表达式函数
# ############################################################
def demo_2_4() -> None:
    print("\n--- 2.4 lambda ---")

    # lambda 只能写"一个表达式"，表达式的值就是返回值，不用写 return
    square: Callable[[float], float] = lambda x: x ** 2
    print(square(5))                     # 25
    print((lambda x, y: x + y)(3, 4))    # 7

    # lambda 最大的价值：作为参数临时传给高阶函数，避免为一次性逻辑单独 def
    students: list[dict[str, Any]] = [
        {"name": "小明", "score": 78.5},
        {"name": "小红", "score": 92.0},
        {"name": "小刚", "score": 65.5},
    ]
    top = max(students, key=lambda s: s["score"])
    print("最高分:", top["name"], f"{top['score']:.1f}")

    # 边界：lambda 里不能写 if 语句块 / for / 赋值 / 多行逻辑。
    #       一旦逻辑超过一行，老老实实用 def，可读性远比"炫技"重要。
    print("""
    判断标准：lambda 体能不能一眼看懂？不能就改 def。
    """)


# ############################################################
# 2.5 高阶函数：接收函数或返回函数的函数
# ############################################################
def demo_2_5_map_filter() -> None:
    print("\n--- 2.5.1 map / filter ---")
    raw: list[str] = ["1", "2.5", "3", "abc", "4"]

    # filter：按条件筛选，返回迭代器（惰性）
    digits: list[str] = list(filter(lambda s: s.replace(".", "", 1).isdigit(), raw))
    print("filter 结果:", digits)

    # map：逐个转换，同样返回迭代器
    nums: list[float] = list(map(float, digits))
    print("map 结果:", nums)

    # 等价且更 Pythonic 的推导式写法（项目里更常见，可读性更好）
    nums2: list[float] = [float(s) for s in raw if s.replace(".", "", 1).isdigit()]
    print("推导式:", nums2, "| 两种写法结果一致:", nums == nums2)

    # 重要陷阱：转换必须放在 try 里或用 filter 先筛，否则 int("abc") 直接崩
    safe: list[float] = []
    for s in raw:
        try:
            safe.append(float(s))
        except ValueError as e:
            print(f"  跳过 {s!r}: {e}")
    print("安全转换:", safe)


def demo_2_5_sorted() -> None:
    print("\n--- 2.5.2 sorted 与 key ---")
    words: list[str] = ["banana", "Apple", "cherry", "date"]

    # 默认按字典序：大写字母 ASCII 更小，所以 Apple 排最前
    print("默认:", sorted(words))
    # key 指定"按什么排序"，这是 sorted 的精髓
    print("忽略大小写:", sorted(words, key=str.lower))
    print("按长度:", sorted(words, key=len))
    print("长度+字典序:", sorted(words, key=lambda w: (len(w), w.lower())))
    print("降序:", sorted(words, key=str.lower, reverse=True))

    # 经典陷阱：对"字符串形式的数字"取最值/排序，比的是字典序不是数值！
    str_nums: list[str] = ["9", "100", "23"]
    print("错误 max:", max(str_nums), "(字典序 '9' > '100')")
    print("正确 max:", max(str_nums, key=float))

    # sorted 不改变原列表，list.sort() 原地修改且返回 None
    data = [3, 1, 2]
    data.sort()
    print("原地 sort 后:", data)


def demo_2_5_any_all_reduce() -> None:
    print("\n--- 2.5.3 any / all / reduce ---")
    scores: list[float] = [88.0, 92.5, 76.0, 100.0]

    # any：有一个为真就 True；all：全为真才 True。短路求值，效率高
    print("是否有人不及格:", any(s < 60 for s in scores))
    print("是否全部优秀(>=85):", all(s >= 85 for s in scores))

    # reduce：把序列"折叠"成一个值，前两个参数是累计值和当前值
    product = reduce(lambda acc, x: acc * x, scores, 1)   # 第三个参数是初始值
    print(f"连乘={product:.3f}")

    # 求和别用 reduce，直接 sum() 更快更清晰；reduce 适合自定义合并逻辑
    merged: dict[str, int] = reduce(
        lambda acc, kv: {**acc, kv[0]: acc.get(kv[0], 0) + kv[1]},
        [("a", 1), ("b", 2), ("a", 3)],
        {},
    )
    print("合并计数:", merged)
    print("  （实际项目直接用 Counter，见下面实战片段）")


# ############################################################
# 2.6 把函数当参数：策略模式，消灭 if-else 长链
# ############################################################
def apply_strategy(value: float, strategy: Callable[[float], float]) -> float:
    """接收一个"处理策略"函数并应用它。

    调用方决定怎么算，被调用方只负责流程 —— 这就是"依赖注入"的雏形。
    """
    return strategy(value)


STRATEGIES: dict[str, Callable[[float], float]] = {
    "round_up": lambda x: -(-x // 1),
    "half": lambda x: x / 2,
    "square": lambda x: x ** 2,
}


def demo_2_6() -> None:
    print("\n--- 2.6 函数作为参数（策略表） ---")
    for name, func in STRATEGIES.items():
        print(f"  {name:9s} -> {apply_strategy(7.5, func):.3f}")
    # 加一种新算法，只需往字典里加一行，不用改任何 if-else


# ############################################################
# ★ 实战片段：订单数据的排序、过滤、聚合统计
# ############################################################
# 场景说明：
#   后台管理系统里最常见的需求："把订单按条件筛出来，按某字段排序，
#   再按用户/商品分组统计金额"。下面用函数式工具链把它写得又短又清楚。
#   真实项目里这些操作可能发生在 ORM（Django QuerySet）或 pandas 上，
#   但思路完全一致：filter -> map -> sort -> group -> aggregate。
# ------------------------------------------------------------
ORDERS: list[dict[str, Any]] = [
    {"id": 1001, "user": "小明", "item": "键盘", "amount": 199.00, "paid": True},
    {"id": 1002, "user": "小红", "item": "鼠标", "amount": 89.50,  "paid": True},
    {"id": 1003, "user": "小明", "item": "显示器", "amount": 1299.00, "paid": False},
    {"id": 1004, "user": "小刚", "item": "键盘", "amount": 199.00, "paid": True},
    {"id": 1005, "user": "小红", "item": "耳机", "amount": None,    "paid": True},
]


def build_report(orders: list[dict[str, Any]],
                 min_amount: float = 0.0,
                 only_paid: bool = True,
                 sort_by: str = "amount",
                 desc: bool = True) -> dict[str, Any]:
    """生成一份订单统计报表。

    :param orders:     原始订单列表
    :param min_amount: 金额下限（低于此值的订单被过滤掉）
    :param only_paid:  是否只统计已支付订单
    :param sort_by:    排序字段，amount / id / user
    :param desc:       是否降序
    :return: {"paid_orders": [...], "top": {...}, "by_user": {...}, "by_item": {...}}
    """
    # --- 1) filter：先清洗。amount 为 None 的脏数据必须排除，否则比较时 TypeError
    cleaned: list[dict[str, Any]] = [
        o for o in orders
        if o.get("amount") is not None
        and (o["paid"] if only_paid else True)
        and o["amount"] >= min_amount
    ]

    # --- 2) sort：key 用 lambda 指定字段，None 已在上一步清掉
    sorted_orders: list[dict[str, Any]] = sorted(
        cleaned, key=lambda o: o[sort_by], reverse=desc
    )

    # --- 3) aggregate：分组求和。用字典累加，注意初始值处理
    by_user: dict[str, float] = {}
    for o in sorted_orders:
        by_user[o["user"]] = by_user.get(o["user"], 0.0) + o["amount"]

    # --- 4) 频次统计：优先用 Counter，比手写遍历简洁且不易出错
    item_counter: Counter[str] = Counter(o["item"] for o in sorted_orders)

    total: float = sum(o["amount"] for o in sorted_orders)   # 中间保持精度
    return {
        "paid_orders": sorted_orders,
        "top": sorted_orders[0] if sorted_orders else None,
        "by_user": by_user,
        "by_item": item_counter,
        "total": total,
        "count": len(sorted_orders),
        "avg": total / len(sorted_orders) if sorted_orders else 0.0,
    }


def practice_report() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段：订单数据 filter -> sort -> group -> aggregate")
    print("=" * 56)

    report: dict[str, Any] = build_report(ORDERS, min_amount=50.0, only_paid=True)

    print(f"命中订单数: {report['count']}")
    print(f"总金额    : {report['total']:.2f}")
    print(f"平均单价  : {report['avg']:.2f}")
    print(f"最大订单  : {report['top']['id']} {report['top']['item']} "
          f"{report['top']['amount']:.2f}")

    print("按用户汇总:")
    for user, amount in sorted(report["by_user"].items(),
                               key=lambda kv: kv[1], reverse=True):
        print(f"    {user:4s} {amount:>10.2f}")

    print("按商品频次:")
    for item, cnt in report["by_item"].most_common():
        print(f"    {item:6s} x{cnt}")

    # 换个排序字段，一行搞定，不用改函数体 —— 这就是"函数作为参数"的收益
    by_id: dict[str, Any] = build_report(ORDERS, sort_by="id", desc=False,
                                         only_paid=False)
    print("按 id 升序(含未支付):", [o["id"] for o in by_id["paid_orders"]])

    print("""
讲解要点：
 1. 脏数据先行：amount 为 None 的记录要在 filter 阶段就剔除。
    统计频次/排序时若不排除 None，会得到 TypeError 或错误结果。
 2. sorted(key=lambda o: o[字段]) 是后台列表页的标配写法，
    字段名做成参数后，前端点哪个表头排序都不用改后端逻辑。
 3. 分组累加用 dict.get(key, 0.0) 处理"第一次出现"，比 try/except KeyError 干净。
 4. 频次统计一律用 collections.Counter，不要用手动字典遍历，
    它自带 most_common()、支持 + - & | 集合运算。
 5. 数值全程不做 round，只在 print 时用 :.2f 格式化，避免精度损失。
 6. build_report 接收 orders 作为参数、返回新字典，不修改入参 ——
    无副作用的函数才好测试、好复用（这也是后面装饰器能"透明增强"的前提）。
""")


# ############################################################
# ★ 实战片段 2：文本清洗 + 词频统计（爬虫/日志分析常用）
# ############################################################
def word_count(text: str, top_n: int = 5,
               stop_words: set[str] | None = None) -> list[tuple[str, int]]:
    """统计文本中单词出现频次，返回前 top_n 个 (词, 次数)。

    用 re 提取 + Counter 统计，比自己写 split/循环可靠得多。
    """
    if stop_words is None:            # 可变默认参数用 None 占位（上一节的知识）
        stop_words = {"the", "a", "an", "of", "to", "in", "is"}

    words: list[str] = re.findall(r"[A-Za-z]+", text.lower())
    filtered: list[str] = [w for w in words if w not in stop_words]
    counter: Counter[str] = Counter(filtered)
    return counter.most_common(top_n)


def practice_word_count() -> None:
    print("\n" + "=" * 56)
    print("★ 实战片段 2：正则 + Counter 词频统计")
    print("=" * 56)
    text: str = ("Python is a great language. Python is easy to read, "
                 "and python code is pythonic. The zen of Python is beautiful.")
    for word, cnt in word_count(text, top_n=5):
        print(f"    {word:10s} {cnt}")
    print("""
讲解要点：
 1. re.findall 负责"切词"，能自动忽略标点，比 text.split() 稳。
 2. Counter.most_common(n) 已经按次数降序排好，不需要再 sorted。
 3. 停用词表用 set 而不是 list：in 判断从 O(n) 降到 O(1)。
 4. 整个函数没有任何副作用，输入字符串 -> 输出列表，非常好写单元测试。
""")


# ############################################################
if __name__ == "__main__":
    demo_1_1()
    demo_1_2()
    demo_2_3()
    demo_2_4()
    demo_2_5_map_filter()
    demo_2_5_sorted()
    demo_2_5_any_all_reduce()
    demo_2_6()
    practice_report()
    practice_word_count()
    print("\n[02 节完] 下一节：03_闭包.py —— 本套课程的分水岭")

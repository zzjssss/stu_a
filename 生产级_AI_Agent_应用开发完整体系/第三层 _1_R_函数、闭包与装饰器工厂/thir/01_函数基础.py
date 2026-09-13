"""
第 01 节 · 函数基础：定义、参数、返回值、注解
======================================================
学习目标
    1. 理解"函数是对象"，可赋值、可传递、可放进容器
    2. 分清 5 种参数形态：位置 / 关键字 / 默认 / *args / **kwargs
    3. 会用 / 和 * 精确控制调用方的传参方式
    4. 避开"可变对象做默认参数"这个头号陷阱
    5. 写出带类型注解 + docstring 的工程级函数
======================================================
"""

from typing import Any


# ############################################################
# 1.1 定义与调用：函数是一等公民
# ############################################################
def greet(name: str) -> str:
    """返回一句问候语。

    :param name: 被问候人的名字
    :return: 拼接好的问候字符串
    """
    return f"你好, {name}!"


def demo_1_1() -> None:
    """演示：函数名只是绑定到函数对象的一个变量。"""
    print("\n--- 1.1 函数是一等公民 ---")

    # (1) 加括号 = 调用，得到返回值；不加括号 = 函数对象本身
    print(greet)            # <function greet at 0x...>
    print(greet("周志杰"))   # 你好, 周志杰!

    # (2) 函数对象可以像普通变量一样赋值
    say_hi = greet
    print(say_hi("同学"))

    # (3) 可以放进列表 / 字典，做"策略表"，这是消灭大量 if-else 的常用手法
    handlers: dict[str, Any] = {"zh": greet, "zh2": greet}
    print(handlers["zh"]("张三"))

    # (4) 函数自带元信息，后面学装饰器时会大量用到
    print("name    :", greet.__name__)
    print("doc     :", greet.__doc__.splitlines()[0])
    print("annotations:", greet.__annotations__)


# ############################################################
# 1.2 四种基本参数：位置、关键字、默认
# ############################################################
def create_user(name: str, age: int, city: str = "广州", vip: bool = False) -> str:
    """创建一个用户描述。

    name / age 是必填的位置参数；
    city / vip 有默认值，调用时可以省略。
    """
    tag = "VIP" if vip else "普通"
    return f"[{tag}] {name}, {age}岁, 来自{city}"


def demo_1_2() -> None:
    print("\n--- 1.2 位置参数 / 关键字参数 / 默认参数 ---")

    # 全按位置传：顺序必须和定义一致
    print(create_user("小明", 18))

    # 按关键字传：顺序随意，可读性最好。项目里参数超过 3 个就该这么写
    print(create_user(age=20, name="小红", vip=True))

    # 混合：位置参数必须写在关键字参数前面，否则 SyntaxError
    print(create_user("小刚", city="深圳", age=22))

    # 注意：默认值只在"函数定义时"求值一次，这是 1.3 陷阱的根源
    print("默认值存放位置:", create_user.__defaults__)   # ('广州', False)


# ############################################################
# 1.3 头号陷阱：可变对象做默认参数
# ############################################################
def add_item_bad(item: str, box: list[str] = []) -> list[str]:
    """错误示范：默认参数是一个"只创建一次"的列表。"""
    box.append(item)
    return box


def add_item_good(item: str, box: list[str] | None = None) -> list[str]:
    """正确写法：默认值用 None 占位，进函数后再创建新对象。"""
    if box is None:          # 一定要用 is None，不要用 == None
        box = []
    box.append(item)
    return box


def demo_1_3() -> None:
    print("\n--- 1.3 可变默认参数陷阱 ---")

    # 期望每次调用都是新列表，实际三次调用共享了同一个列表！
    print(add_item_bad("苹果"))   # ['苹果']
    print(add_item_bad("香蕉"))   # ['苹果', '香蕉']  <-- 脏数据
    print(add_item_bad("橘子"))   # ['苹果', '香蕉', '橘子']
    print("被共享的默认值:", add_item_bad.__defaults__)

    # 正确版本互不干扰
    print(add_item_good("苹果"))  # ['苹果']
    print(add_item_good("香蕉"))  # ['香蕉']

    # 同理适用于 dict / set。规则一句话：
    # 默认值永远只用不可变对象（None / int / str / tuple / frozenset / bool）


# ############################################################
# 1.4 *args 与 **kwargs：不定长参数
# ############################################################
def summarize(*args: float, **kwargs: Any) -> None:
    """*args 收集"多余的位置参数"成元组；**kwargs 收集"多余的关键字参数"成字典。"""
    print("args   :", args, type(args).__name__)
    print("kwargs :", kwargs, type(kwargs).__name__)
    if args:
        total = sum(args)
        avg = total / len(args)
        # 输出统一保留 3 位小数，用 f-string 的 :.3f 而不是 round()
        print(f"合计={total:.3f}, 平均={avg:.3f}")


def demo_1_4() -> None:
    print("\n--- 1.4 *args / **kwargs ---")
    summarize(1.5, 2, 3.5, name="周志杰", role="学生")

    # 反向用法：解包（unpacking）。把容器"摊平"成实参
    nums: list[float] = [10.0, 20.0, 30.0]
    info: dict[str, Any] = {"name": "李四", "role": "老师"}
    summarize(*nums, **info)

    # 定义顺序永远是：位置参数 -> *args -> 仅关键字参数 -> **kwargs
    def mixed(a: int, *args: int, flag: bool = False, **kwargs: Any) -> str:
        return f"a={a}, args={args}, flag={flag}, kwargs={kwargs}"

    print(mixed(1, 2, 3, flag=True, x=9, y=8))


# ############################################################
# 1.5 / 与 *：强制调用方按你期望的方式传参
# ############################################################
def divide(a: float, b: float, /, *, precision: int = 2) -> str:
    """a、b 只能按位置传（/ 左边）；precision 只能按关键字传（* 右边）。

    这样设计的好处：
      · 防止调用方写 divide(b=1, a=2) 改变语义，也方便以后重命名参数
      · precision 强制写名字，避免 divide(1, 2, 3) 这种看不懂 3 是什么的调用
    """
    return f"{a / b:.{precision}f}"


def demo_1_5() -> None:
    print("\n--- 1.5 仅位置 / 仅关键字 ---")
    print(divide(10, 3))                  # OK
    print(divide(10, 3, precision=4))     # OK
    try:
        print(divide(a=10, b=3))          # TypeError: 仅位置参数不能按关键字传
    except TypeError as e:
        print("报错1:", e)
    try:
        print(divide(10, 3, 4))           # TypeError: 仅关键字参数不能按位置传
    except TypeError as e:
        print("报错2:", e)


# ############################################################
# 1.6 返回值：可以没有、可以一个、可以多个
# ############################################################
def no_return() -> None:
    """不写 return 或写 return（不带值），都会返回 None。"""
    print("我只做事，不返回")


def min_max(nums: list[float]) -> tuple[float, float]:
    """返回多个值，本质是返回一个元组。"""
    return min(nums), max(nums)


def demo_1_6() -> None:
    print("\n--- 1.6 返回值 ---")
    print("no_return() 的返回值:", no_return())

    data = [3.2, 1.1, 9.8, 4.5]
    # 方式一：整体接收
    result = min_max(data)
    print("元组:", result)
    # 方式二：解包接收（更常用）
    lo, hi = min_max(data)
    print(f"最小={lo:.3f}, 最大={hi:.3f}")
    # 方式三：不关心的值用 _ 占位
    _, only_max = min_max(data)
    print(f"只要最大值={only_max:.3f}")


# ############################################################
# 1.7 类型注解 + docstring：工程里的标准写法
# ############################################################
def calc_bmi(weight_kg: float, height_m: float) -> tuple[float, str]:
    """根据体重(kg)与身高(m)计算 BMI 并给出等级。

    计算过程保留完整精度，只在最后输出时格式化成 1 位小数，
    避免中间步骤 round 造成误差累积。

    :param weight_kg: 体重，单位千克，必须 > 0
    :param height_m: 身高，单位米，必须 > 0
    :return: (bmi 数值, 等级描述)
    :raises ValueError: 当体重或身高不是正数时抛出
    """
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("体重和身高必须为正数")

    bmi = weight_kg / (height_m ** 2)   # 中间不 round
    if bmi < 18.5:
        level = "偏瘦"
    elif bmi < 24:
        level = "正常"
    elif bmi < 28:
        level = "偏胖"
    else:
        level = "肥胖"
    return bmi, level


def demo_1_7() -> None:
    print("\n--- 1.7 注解与 docstring ---")
    bmi, level = calc_bmi(70.0, 1.75)
    print(f"BMI={bmi:.1f} -> {level}")       # 输出时才格式化

    # 注解不影响运行（Python 是动态类型），但能让 PyCharm / mypy 提前发现错误
    print("函数签名注解:", calc_bmi.__annotations__)

    # 异常也要会处理：捕获 Exception 并把详细信息打出来，方便排查
    try:
        calc_bmi(-1, 1.7)
    except Exception as e:
        print(f"捕获异常: {type(e).__name__}: {e}")


# ############################################################
# ★ 实战片段：接口请求参数解析与校验
# ############################################################
# 场景说明：
#   Web 项目里，前端传来的参数全是字符串（"18"、"true"、"95.5"），
#   而业务代码需要 int / bool / float。所以每个接口入口都要做
#   "取值 -> 类型转换 -> 范围校验 -> 给默认值"这一套。
#   下面这个函数就是这套逻辑的标准模板，Flask / Django 项目里几乎天天写。
# ------------------------------------------------------------
def parse_query(params: dict[str, str], key: str,
                cast: type = str, default: Any = None,
                required: bool = False) -> Any:
    """从请求参数字典中安全地取出一个值并完成类型转换。

    :param params:   原始请求参数，例如 {"page": "2", "size": "20"}
    :param key:      要取的参数名
    :param cast:     目标类型（int / float / bool / str）
    :param default:  取不到或转换失败时使用的默认值
    :param required: 为 True 且参数缺失时直接抛错
    :return:         转换后的值
    """
    raw: str | None = params.get(key)

    # 1) 缺失处理
    if raw is None or raw == "":
        if required:
            raise ValueError(f"缺少必填参数: {key}")
        return default

    # 2) bool 特殊处理：非空字符串 bool("false") 会得到 True，必须自己映射
    if cast is bool:
        return raw.strip().lower() in ("1", "true", "yes", "y", "on")

    # 3) 其他类型：转换必须写在 try 里，否则 "abc" 转 int 会直接崩掉整个请求
    try:
        return cast(raw)
    except (ValueError, TypeError) as e:
        print(f"[WARN] 参数 {key}={raw!r} 转 {cast.__name__} 失败: {e}，使用默认值")
        return default


def practice_api_params() -> None:
    """实战：解析一个"分页查询商品"接口的参数。"""
    print("\n" + "=" * 56)
    print("★ 实战片段：接口参数解析与校验")
    print("=" * 56)

    # 模拟前端真实传来的东西：全是字符串，还有脏数据
    query: dict[str, str] = {
        "keyword": "手机",
        "page": "3",
        "size": "abc",        # 脏数据 -> 应回退到默认值而不是崩溃
        "on_sale": "true",
        "max_price": "2999.9",
    }

    keyword: str = parse_query(query, "keyword", str, default="")
    page: int = parse_query(query, "page", int, default=1)
    size: int = parse_query(query, "size", int, default=20)
    on_sale: bool = parse_query(query, "on_sale", bool, default=False)
    max_price: float = parse_query(query, "max_price", float, default=0.0)

    # 业务校验：分页大小限制在 1~100，防止有人传 size=999999 打爆数据库
    size = max(1, min(size, 100))
    page = max(1, page)

    print(f"keyword   = {keyword!r} ({type(keyword).__name__})")
    print(f"page      = {page} ({type(page).__name__})")
    print(f"size      = {size} ({type(size).__name__})")
    print(f"on_sale   = {on_sale} ({type(on_sale).__name__})")
    print(f"max_price = {max_price:.2f} ({type(max_price).__name__})")

    # required=True 的用法：缺参数就直接 400
    try:
        parse_query({"page": "1"}, "user_id", int, required=True)
    except Exception as e:
        print(f"必填校验: {type(e).__name__}: {e}")

    print("""
讲解要点：
 1. cast: type = str 把"类型"当参数传进来 —— 这就是"函数是一等公民"的直接收益，
    类型对象 int/float/bool 可以像普通值一样被传递和调用。
 2. bool 必须单独处理，这是新手最常踩的坑：bool("false") == True。
 3. 类型转换一定要包在 try 里，并且 except 要写具体异常 + 打印详细信息。
 4. 校验和"夹紧"(clamp)分开写：先转换，再限制范围，代码职责清晰。
 5. 这套函数写好后，整个项目所有接口都能复用，这就是函数抽象的价值。
""")


# ############################################################
if __name__ == "__main__":
    demo_1_1()
    demo_1_2()
    demo_1_3()
    demo_1_4()
    demo_1_5()
    demo_1_6()
    demo_1_7()
    practice_api_params()
    print("\n[01 节完] 下一节：02_作用域与一等公民.py")

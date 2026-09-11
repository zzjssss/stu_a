"""
第 2 讲 可变 vs 不可变

不可变：int, float, bool, str, tuple, frozenset, bytes, None
可  变：list, dict, set, bytearray, 以及绝大多数自定义类的实例

学习目标：
  1) 用 id() 验证"修改不可变对象其实是新建对象"
  2) 搞懂 Python 的传参模型（对象引用传递 / call by sharing）
  3) 彻底理解可变默认参数、tuple 半可变、深浅拷贝三大坑
"""
import copy
import time
from typing import Any

import pydantic

IMMUTABLE_EXAMPLES: tuple[Any, ...] = (
    1, 3.14, True, None, "abc", (1, 2), frozenset({1, 2}), b"bytes",
)
MUTABLE_EXAMPLES: tuple[Any, ...] = (
    [1], {1, 2}, {"k": 1}, bytearray(b"ab"),
)


def is_hashable(obj: Any) -> bool:
    """可变对象一律不可哈希，因此不能当 dict 的 key 或 set 的元素。"""
    try:
        hash(obj)
        return True
    except TypeError:
        return False


def demo_1_overview() -> None:
    print("=" * 66)
    print("2.1 用 hash() 区分可变/不可变")
    for obj in IMMUTABLE_EXAMPLES:
        print(f"  不可变 {type(obj).__name__:<12}{str(obj):<16}可哈希 = {is_hashable(obj)}")
    for obj in MUTABLE_EXAMPLES:
        print(f"  可  变 {type(obj).__name__:<12}{str(obj):<16}可哈希 = {is_hashable(obj)}")
    print("  >> 嵌套了 list 的 tuple 也不可哈希：")
    print(f"     ([1], ) 可哈希 = {is_hashable(([1],))}")


def demo_2_rebuild() -> None:
    print("=" * 66)
    print("2.2 不可变对象的"修改"= 新建对象；可变对象的 += 是原地")

    s = "abc"
    id_before = id(s)
    s = s + "d"
    print(f"  str   : s = s + 'd'    -> id 变了吗? {id_before != id(s)}")

    t = (1, 2)
    id_before = id(t)
    t = t + (3,)
    print(f"  tuple : t = t + (3,)   -> id 变了吗? {id_before != id(t)}")

    lst = [1, 2]
    id_before = id(lst)
    lst += [3]                      # 调 __iadd__，原地扩展
    same_after_iadd = id_before == id(lst)
    lst = lst + [4]                 # 调 __add__，新建列表
    print(f"  list  : lst += [3]     -> id 没变吗? {same_after_iadd}")
    print(f"  list  : lst = lst + [4]-> id 变了吗? {id_before != id(lst)}")
    print("  >> += 和 = ... + 对 list 来说不是一回事，这是高频面试题。")


def append_to(data: list[int]) -> None:
    data.append(99)          # 原地修改：外部可见


def rebind_local(data: list[int]) -> None:
    data = [7, 8, 9]         # 只是让局部名字指向新对象：外部毫发无伤


def bump(num: int) -> None:
    num += 1                 # int 不可变，等价于局部重绑定


def demo_3_pass_model() -> None:
    print("=" * 66)
    print("2.3 传参模型：传的是"对象引用的副本"，既不是值也不是引用")

    a = [1, 2]
    append_to(a)
    print(f"  append_to(a)    后 a = {a}     <- 被改了")

    b = [1, 2]
    rebind_local(b)
    print(f"  rebind_local(b) 后 b = {b}           <- 没被改")

    c = 10
    bump(c)
    print(f"  bump(c)         后 c = {c}              <- 没被改")
    print("  >> 判断法则：函数里对参数"点方法原地改"会影响外部；"= 赋值"永远不影响外部。")


def bad_add(item: str, box: list = []) -> list:   # PyCharm 会警告，这个警告是对的！
    box.append(item)
    return box


def good_add(item: str, box: list[str] | None = None) -> list[str]:
    if box is None:
        box = []
    box.append(item)
    return box


def demo_4_default_arg() -> None:
    print("=" * 66)
    print("2.4 可变默认参数陷阱（你之前踩过，这里从"对象"角度再解释一次）")
    print(f"  bad_add('a')  -> {bad_add('a')}")
    print(f"  bad_add('b')  -> {bad_add('b')}      <- 累积了！")
    print(f"  bad_add('c')  -> {bad_add('c')}")
    print(f"  默认对象 id 一直不变: {bad_add.__defaults__[0] is bad_add.__defaults__[0]}")
    print(f"  good_add('a') -> {good_add('a')}")
    print(f"  good_add('b') -> {good_add('b')}")
    print("  >> 默认值在"函数定义时"创建一次，存在 __defaults__ 里，所有调用共享。")


def demo_5_tuple_half_mutable() -> None:
    print("=" * 66)
    print("2.5 tuple 的"半可变"：tuple 只保证引用不变，不保证引用对象内容不变")

    t: tuple[list[int], ...] = ([1, 2],)
    t[0].append(3)
    print(f"  t[0].append(3) 合法 -> t = {t}")
    try:
        t[0] = [9]                     # type: ignore[misc]
    except TypeError as e:
        print(f"  t[0] = [9]        -> TypeError: {e}")

    t2: tuple[list[int], ...] = ([1, 2],)
    try:
        t2[0] += [3]                   # 先原地扩展成功，再赋值失败
    except TypeError as e:
        print(f"  t2[0] += [3]      -> TypeError: {e}")
    print(f"  但 t2 竟然已经变了 -> {t2}")
    print("  >> 经典反直觉：异常抛出了，副作用却留下了。别在 tuple 里塞可变对象。")


def demo_6_copy() -> None:
    print("=" * 66)
    print("2.6 浅拷贝 vs 深拷贝")

    scores: list[list[Any]] = [["张三", 85], ["李四", 92]]
    shallow = scores.copy()            # 也可写 list(scores) 或 scores[:]
    deep = copy.deepcopy(scores)

    scores[0].append("新字段")          # 改内层对象
    print(f"  原     : {scores}")
    print(f"  浅拷贝 : {shallow}   <- 内层跟着变")
    print(f"  深拷贝 : {deep}")

    shallow.append(["王五", 60])         # 改外层结构
    print(f"  shallow.append 后：原 {len(scores)} 项，浅 {len(shallow)} 项  <- 外层是独立的")
    print("  >> 浅拷贝：新外壳 + 共享内层；深拷贝：整棵树全复制。")


def demo_7_perf() -> None:
    print("=" * 66)
    print("2.7 不可变带来的性能问题：循环里用 += 拼字符串是 O(n²)")

    chars = ["a"] * 50_000

    start = time.perf_counter()
    s = ""
    for c in chars:
        s += c                          # 每次都新建一个更长的字符串
    slow = time.perf_counter() - start

    start = time.perf_counter()
    s2 = "".join(chars)                 # 一次算好总长度，一次分配
    fast = time.perf_counter() - start

    print(f"  += 拼接 : {slow * 1000:8.1f} ms")
    print(f"  join    : {fast * 1000:8.2f} ms")
    print(f"  结果一致: {s == s2}")
    print("  >> 你 work.py 里 word_count 的 str_s += ch 就是这个模式，改用列表收集 + ''.join 更快。")


if __name__ == "__main__":
    demo_1_overview()
    demo_2_rebuild()
    demo_3_pass_model()
    demo_4_default_arg()
    demo_5_tuple_half_mutable()
    demo_6_copy()
    demo_7_perf()
    print("=" * 66)
    print("""本讲规则清单：
  1. 不可变：int float bool str tuple frozenset bytes None
  2. 可哈希 ⟺ 不可变（或自定义 __hash__），才能当 dict key / set 元素
  3. 函数内 obj.append()/obj[k]=v 会影响外部；obj = ... 不会
  4. 默认参数永不用 list/dict/set，用 None 兜底
  5. tuple 里别放 list；需要不可变序列就全用不可变元素
  6. 嵌套结构复制想清楚要浅拷贝还是 deepcopy
  7. 大量字符串拼接用 ''.join()""")

   ======================================================================


    """
第 3 讲 鸭子类型（Duck Typing）

"If it walks like a duck and quacks like a duck, it must be a duck."

Java/C++ 的思路（名义类型）：必须先 implements 某个接口，才能传进去。
Python 的思路（结构类型）：只要你有我要调的那个方法，你就是我要的类型。

学习目标：
  1) 理解"协议(protocol)"这个概念：__len__ / __iter__ / __enter__ ...
  2) 掌握 EAFP（先做再说）优于 LBYL（先问再做）
  3) 用 typing.Protocol 把鸭子类型"静态化"，既灵活又有 IDE 检查
"""
import time
from typing import Any, Iterator, Protocol, runtime_checkable


# ---------- 3.1 名义类型 vs 结构类型 ----------

class Duck:
    def speak(self) -> str:
        return "嘎嘎嘎"


class Dog:
    def speak(self) -> str:
        return "汪汪汪"


class Robot:
    def speak(self) -> str:
        return "哔哔哔"


@runtime_checkable
class Speaker(Protocol):
    """结构类型：任何"有 speak() -> str 方法"的类，自动就是 Speaker。"""

    def speak(self) -> str: ...


def announce(who: Speaker) -> None:
    print(f"  {who.speak()}")


def demo_1_duck() -> None:
    print("=" * 66)
    print("3.1 三个毫无继承关系的类，被同一个函数接受")
    for obj in (Duck(), Dog(), Robot()):
        announce(obj)
    print(f"  isinstance(Duck(), Speaker)   -> {isinstance(Duck(), Speaker)}")
    print(f"  isinstance(object(), Speaker) -> {isinstance(object(), Speaker)}")
    print("  >> Duck 从没写过 class Duck(Speaker)，但它"结构上"满足 Protocol。")


# ---------- 3.2 协议：实现 __xxx__ 就自动融入语言 ----------

class Playlist:
    """只实现 3 个魔术方法，就能 len() / [] / for / in / reversed()。"""

    def __init__(self, *songs: str) -> None:
        self._songs: list[str] = list(songs)

    def __len__(self) -> int:
        return len(self._songs)

    def __getitem__(self, index: int) -> str:
        return self._songs[index]

    def __contains__(self, song: object) -> bool:
        return song in self._songs

    def __repr__(self) -> str:
        return f"Playlist({self._songs!r})"


class Timer:
    """实现 __enter__ / __exit__ 就自动支持 with 语句。"""

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.cost = (time.perf_counter() - self.start) * 1000
        print(f"  耗时 {self.cost:.3f} ms")


def countdown(n: int) -> Iterator[int]:
    """实现"生成器协议"：有 __next__ 和 __iter__，就是迭代器。"""
    while n > 0:
        yield n
        n -= 1


def demo_2_protocol() -> None:
    print("=" * 66)
    print("3.2 协议就是"一组魔术方法的约定"")

    pl = Playlist("晴天", "稻香", "夜曲")
    print(f"  len(pl)        -> {len(pl)}          (靠 __len__)")
    print(f"  pl[0], pl[-1]  -> {pl[0]}, {pl[-1]}   (靠 __getitem__)")
    print(f"  '稻香' in pl   -> {'稻香' in pl}          (靠 __contains__)")
    print(f"  list(reversed) -> {list(reversed(pl))}   (靠 __len__ + __getitem__)")
    print("  for song in pl  -> ", end="")
    for song in pl:
        print(song, end=" ")
    print()

    print("  with Timer():")
    with Timer():
        sum(range(1_000_000))

    print(f"  生成器协议: {list(countdown(3))}")
    print("  >> 你不需要继承任何基类，只要"长得像"，内置函数就认。")


# ---------- 3.3 EAFP vs LBYL ----------

class FakeFile:
    def read(self) -> str:
        return "<文件内容>"


def read_source_lbyl(obj: Any) -> str:
    """LBYL: Look Before You Leap —— 先检查再动手（不够 Pythonic）"""
    if hasattr(obj, "read"):
        return obj.read()
    return str(obj)


def read_source_eafp(obj: Any) -> str:
    """EAFP: Easier to Ask Forgiveness than Permission —— 先动手，出事再兜"""
    try:
        return obj.read()
    except AttributeError:
        return str(obj)


def demo_3_eafp() -> None:
    print("=" * 66)
    print("3.3 EAFP 优于 LBYL")
    for obj in (FakeFile(), "普通字符串", 42):
        print(f"  {str(obj):<12} LBYL -> {read_source_lbyl(obj):<12} EAFP -> {read_source_eafp(obj)}")
    print("  >> LBYL 有竞态风险且代码啰嗦；EAFP 更符合鸭子类型精神。")


# ---------- 3.4 鸭子类型的翻车现场 ----------    就是只看方法名   不看方法标签

class OrderItem:
    def __init__(self, price: float, count: int) -> None:
        self.price = price
        self.count = count


def total_price(items: Any) -> float:
    return sum(item.price * item.count for item in items)


def demo_4_crash() -> None:
    print("=" * 66)
    print("3.4 鸭子类型的代价：错误信息在函数深处，很难定位")
    print(f"  传 OrderItem 列表 -> {total_price([OrderItem(9.9, 2), OrderItem(5.0, 1)])}")
    try:
        total_price([{"price": 9.9, "count": 2}])   # 手滑传了 dict
    except AttributeError as e:
        print(f"  传 dict 列表     -> AttributeError: {e}")
    print("  >> 解法：给 items 加 Protocol 注解，PyCharm 在"调用处"就标红。见 3.5。")


class Priced(Protocol):
    price: float
    count: int


def total_price_safe(items: list[Priced]) -> float:
    return sum(item.price * item.count for item in items)


def demo_5_protocol_fix() -> None:
    print("=" * 66)
    print("3.5 Protocol 让鸭子类型可被静态检查")
    print(f"  total_price_safe([OrderItem(...)]) -> {total_price_safe([OrderItem(9.9, 2)])}")
    print("  现在把 total_price_safe([{'price': 1}]) 写出来，PyCharm 直接标红：")
    print("    Expected type 'list[Priced]', got 'list[dict[str, int]]' instead")
    print("  >> Protocol 描述"能做什么"，class 描述"是什么"。前者才是 Python 的灵魂。")


if __name__ == "__main__":
    demo_1_duck()
    demo_2_protocol()
    demo_3_eafp()
    demo_4_crash()
    demo_5_protocol_fix()
    print("=" * 66)
    print("""本讲要点：
  1. Python 不检查"是不是某个类"，只检查"有没有某个行为"
  2. 协议 = 一组魔术方法的约定：__len__ __getitem__ __iter__ __enter__ __add__ ...
  3. EAFP：try/except 比 hasattr/if 更 Pythonic
  4. isinstance 只该用在：输入边界校验、分派本质不同的类型（int/str/bytes）
  5. typing.Protocol = 静态化的鸭子类型，兼得灵活性与 IDE 检查""")






++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
第 4 讲 渐进式类型注解（Gradual Typing）

"渐进式"三个字的含义：
  - 你可以只给一部分代码加注解，其余保持动态类型，两者共存
  - 注解可以从粗到细逐步收紧：先 Any，再 list，再 list[dict[str, int]]
  - 检查是"外挂"的（PyCharm / mypy / pyright），解释器本身不管

本文件故意【不】写 from __future__ import annotations，
以便演示 Python 3.13 下注解是"立即求值"的这一事实。
"""
from typing import Any, get_type_hints


# ---------- 4.1 注解的四种位置 ----------

MODULE_CONST: int = 42                       # ① 模块级变量


class Person(pydantic.BaseModel):
    species: str = "Homo sapiens"            # ② 类属性（注意：这是类变量，不是实例注解）

    def __init__(self, name: str, age: int) -> None:   # ③④ 参数 + 返回值
        self.name: str = name                # ⑤ 实例属性
        self.age: int = age
        self.tags: list[str] = []


def demo_1_syntax() -> None:
    print("=" * 66)
    print("4.1 注解可以写在哪")
    p = Person("周志杰", 20)
    print(f"  {p.name}, {p.age}, {p.tags}")
    print(f"  Person.__init__.__annotations__ = {Person.__init__.__annotations__}")
    print(f"  Person.__annotations__          = {Person.__annotations__}")
    print("  >> 全部只是字典里的元数据，运行时可读取，但不产生任何约束。")


# ---------- 4.2 内置泛型（3.9+），别再写 typing.List ----------

def stats(nums: list[int]) -> dict[str, float]:
    return {
        "min": float(min(nums)),
        "max": float(max(nums)),
        "avg": sum(nums) / len(nums),
    }


def nested(data: dict[str, list[tuple[int, str]]]) -> set[str]:
    return {s for pairs in data.values() for _, s in pairs}


def demo_2_builtin_generics() -> None:
    print("=" * 66)
    print("4.2 Python 3.9+ 直接用小写内置类型做泛型")
    print(f"  stats([85, 92, 68]) -> {stats([85, 92, 68])}")
    print(f"  nested(...)         -> {nested({'a': [(1, 'x'), (2, 'y')]})}")
    print("""  ✅ list[int]  dict[str, int]  tuple[str, int]  set[str]  type[int]
  ❌ typing.List / Dict / Tuple / Set 从 3.9 起已"软弃用"，只用于兼容 3.8""")


# ---------- 4.3 可选值与联合类型 ----------

USERS: dict[int, dict[str, Any]] = {1: {"name": "张三", "score": 85}}


def find_user(uid: int) -> dict[str, Any] | None:
    return USERS.get(uid)


def parse_id(value: int | str) -> int:
    return int(value)


def demo_3_optional() -> None:
    print("=" * 66)
    print("4.3 X | None 与 X | Y（3.10+ 语法，等价于 Union[X, Y]）")

    user = find_user(1)
    print(f"  find_user(1) -> {user}")
    if user is not None:                # ← 这一步叫"类型收窄"(narrowing)
        print(f"  收窄后 PyCharm 知道 user 是 dict，可以放心 user['name'] = {user['name']}")

    missing = find_user(999)
    print(f"  find_user(999) -> {missing}")
    if missing is None:
        print("  收窄后 PyCharm 知道这里是 None，写 missing['name'] 会标红")

    print(f"  parse_id('42') -> {parse_id('42')}")
    print("  >> Optional[str] 的意思是 str | None，【不是】"这个参数可以省略"！")


# ---------- 4.4 前向引用：3.13 的注解是立即求值的 ----------

def demo_4_forward_reference() -> None:
    print("=" * 66)
    print("4.4 前向引用陷阱（Python 3.13 及以前，注解在 def 执行时就求值）")

    broken = """
class Node:
    def __init__(self, next_node: Node | None = None):
        self.next_node = next_node
"""
    try:
        exec(broken)
    except NameError as e:
        print(f"  类里直接引用自己 -> NameError: {e}")

    print("""  三种修法：
    ① 加引号变字符串：next_node: "Node | None" = None
    ② 文件第一行写：from __future__ import annotations   （推荐，PEP 563）
    ③ 升级到 Python 3.14（PEP 649 默认延迟求值）""")


class Node:
    """演示修法 ①：用字符串注解。"""

    def __init__(self, value: int, next_node: "Node | None" = None) -> None:
        self.value = value
        self.next_node = next_node

    def __repr__(self) -> str:
        return f"Node({self.value}, next={self.next_node!r})"


# ---------- 4.5 __annotations__ 是字符串时，用 get_type_hints 解析 ----------

def query(sql: "str", params: "list[Any]") -> "dict[str, Any]":
    return {"sql": sql, "params": params}


def demo_5_introspection() -> None:
    print("=" * 66)
    print("4.5 运行时读取注解")
    print(f"  query.__annotations__   -> {query.__annotations__}")
    print(f"  get_type_hints(query)   -> {get_type_hints(query)}")
    n = Node(1, Node(2))
    print(f"  链表演示: {n}")
    print("  >> __annotations__ 可能存的是字符串；get_type_hints() 帮你解析成真实类型对象。")


# ---------- 4.6 Any vs object vs 不写 ----------

def take_any(x: Any) -> Any:
    return x.whatever_method()      # 检查器完全放弃，随便你调（运行时才会炸）


def take_object(x: object) -> str:
    return str(x)                   # 只能做所有对象都支持的操作：str/repr/==/hash


def take_nothing(x) -> None:        # 不写注解 ≈ 隐式 Any，但语义是"我还没想好"
    print(f"  take_nothing 收到 {x!r}")


def demo_6_any_object() -> None:
    print("=" * 66)
    print("4.6 Any / object / 不写注解 的区别")
    print(f"  take_object([1, 2]) -> {take_object([1, 2])}")
    take_nothing(1)
    try:
        take_any(1)
    except AttributeError as e:
        print(f"  take_any(1) -> AttributeError: {e}   (Any 让检查器闭嘴，但救不了运行时)")
    print("""  >> Any  = 双向兼容，彻底关闭检查（逃生舱，少用）
  >> object = 什么都能传进来，但函数体内只能用通用操作（更安全）
  >> 不写   = 隐式 Any，渐进式迁移时先留着，之后再补""")


# ---------- 4.7 渐进式落地路线图 ----------

def demo_7_roadmap() -> None:
    print("=" * 66)
    print("4.7 渐进式迁移的推荐顺序")
    print("""  第 0 步：什么都不写（你现在的状态）
  第 1 步：给"公共函数/被别人调用的函数"补参数和返回值类型
  第 2 步：给复杂数据结构补类型（优先用 TypedDict / dataclass 替代裸 dict）
  第 3 步：文件首行加 from __future__ import annotations
  第 4 步：开启 PyCharm 严格检查，或装 mypy：
             pip install mypy
             mypy --strict 你的目录
  第 5 步：内部小函数交给 IDE 自动推断，不强行注解（过度注解反而降低可读性）""")


if __name__ == "__main__":
    demo_1_syntax()
    demo_2_builtin_generics()
    demo_3_optional()
    demo_4_forward_reference()
    demo_5_introspection()
    demo_6_any_object()
    demo_7_roadmap()
    print("=" * 66)
    print("本讲要点：注解不强制、可渐进、给工具看；3.13 下注解立即求值，递归引用要加引号。")









    =======================================================
    """
第 5 讲 typing 模块核心用法（Python 3.13）

覆盖：Literal / Final / TypeAlias / type 语句 / NewType
      抽象容器 Iterable·Sequence·Mapping / Callable
      TypeVar 泛型函数 / PEP 695 新语法 / Generic 泛型类
      TypedDict / NamedTuple / dataclass
      overload / NoReturn / Never / assert_never / Self / cast
"""
from __future__ import annotations   # 放第一行（docstring 之后），全文件注解延迟求值

import json
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Final,
    Iterable,
    Literal,
    Mapping,
    NamedTuple,
    NewType,
    NoReturn,
    Self,
    Sequence,
    TypedDict,
    TypeVar,
    assert_never,
    cast,
    overload,
)

# ================= 5.1 基础组合类型 =================

MAX_RETRY: Final[int] = 3                      # Final：不允许再赋值，检查器会拦
Grade = Literal["A", "B", "C", "D", "F"]       # 字面量类型：只能是这几个值
UserId = NewType("UserId", int)                # NewType：造一个"语义上不同"的 int

# 类型别名的两种写法
ScoresAlias = list[dict[str, int]]             # 旧写法（隐式别名）
StudentMap: TypeAlias = dict[str, int]         # 3.10+ 显式别名
type ScoreList = list[int]                     # 3.12+ PEP 695，最推荐

StudentId = int
StudentName = str


def demo_1_basic() -> None:
    print("=" * 66)
    print("5.1 Literal / Final / NewType / 类型别名")

    uid = UserId(1001)
    order_id = NewType("OrderId", int)(1001)
    print(f"  UserId(1001) = {uid}, type = {type(uid).__name__}")
    print(f"  运行时 UserId 和 OrderId 都是 int，检查器却认为它们不能互相赋值")
    print(f"  MAX_RETRY = {MAX_RETRY}")
    print(f"  ScoreList 别名 = {ScoreList}")

    def to_grade(score: int) -> Grade:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    print(f"  to_grade(92) = {to_grade(92)}")
    print("  >> 写 return 'E' 会被标红，因为 'E' 不是 Grade 的成员。")


# ================= 5.2 具体容器 vs 抽象容器 =================

def sum_iterable(nums: Iterable[int]) -> int:
    """入参用抽象类型（宽容）：list / tuple / set / 生成器 / 自定义可迭代都能传。"""
    return sum(nums)


def top_score(scores: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Sequence 支持 len() 和 []；Mapping 支持只读的 []、keys()。"""
    return max(scores, key=lambda s: s["score"])


def build_index(students: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    return {s["name"]: s["score"] for s in students}


def demo_2_containers() -> None:
    print("=" * 66)
    print("5.2 黄金法则：参数用抽象类型，返回值用具体类型")

    data = [("张三", 85), ("李四", 92)]
    print(f"  sum_iterable([1,2,3])          -> {sum_iterable([1, 2, 3])}")
    print(f"  sum_iterable((1,2,3))          -> {sum_iterable((1, 2, 3))}")
    print(f"  sum_iterable(x*2 for x in ...) -> {sum_iterable(x * 2 for x in range(4))}")

    scores = [{"name": n, "score": s} for n, s in data]
    print(f"  top_score(...)  -> {top_score(scores)}")
    print(f"  build_index(...) -> {build_index(scores)}")
    print("""  对照表：
    具体（能构造、能改）        抽象（只描述能力，来自 collections.abc）
    list[T]                    Sequence[T] / Iterable[T] / MutableSequence[T]
    dict[K, V]                 Mapping[K, V]（只读） / MutableMapping[K, V]
    set[T]                     AbstractSet[T] / Container[T]
    tuple[str, int]  定长       tuple[int, ...]  变长同质""")


# ================= 5.3 Callable =================

def sort_by[T](items: list[T], key: Callable[[T], Any], reverse: bool = False) -> list[T]:
    return sorted(items, key=key, reverse=reverse)


def apply_all(value: int, funcs: Sequence[Callable[[int], int]]) -> list[int]:
    return [f(value) for f in funcs]


def demo_3_callable() -> None:
    print("=" * 66)
    print("5.3 Callable[[参数类型...], 返回类型]")
    students = [{"name": "张三", "score": 85}, {"name": "李四", "score": 92}]
    print(f"  按分数降序 -> {sort_by(students, key=lambda s: s['score'], reverse=True)}")
    print(f"  apply_all(5, [lambda x: x+1, lambda x: x*2]) -> {apply_all(5, [lambda x: x + 1, lambda x: x * 2])}")
    print("""  Callable[..., Any]  参数不定
      Callable[[], None] 无参无返回""")


# ================= 5.4 TypeVar 与泛型函数 =================

T = TypeVar("T")                       # 经典写法
NumT = TypeVar("NumT", int, float)     # 约束：只能是 int 或 float（各自独立解析）
SizedT = TypeVar("SizedT", bound=Sequence[Any])   # 上界：必须是 Sequence 的子类型


def first(items: Sequence[T]) -> T:
    """没有 TypeVar 就得写 -> Any，调用方拿到结果后 IDE 什么都不知道。"""
    return items[0]


def pair(a: T, b: T) -> tuple[T, T]:
    """T 出现两次 = 强制两个参数是同一种类型。"""
    return (a, b)


def double(n: NumT) -> NumT:
    return n * 2


# PEP 695 新语法（3.12+），不用再手动 TypeVar
def last[U](items: Sequence[U]) -> U:
    return items[-1]


def demo_4_typevar() -> None:
    print("=" * 66)
    print("5.4 TypeVar：把"输入类型"和"输出类型"关联起来")
    nums = [1, 2, 3]
    words = ["a", "b"]
    print(f"  first(nums)  = {first(nums)!r}   <- 检查器推断为 int")
    print(f"  first(words) = {first(words)!r}   <- 检查器推断为 str")
    print(f"  pair(1, 2)   = {pair(1, 2)}")
    print(f"  double(3)    = {double(3)}, double(1.5) = {double(1.5)}")
    print(f"  last(nums)   = {last(nums)}")
    try:
        print(pair(1, "x"))     # 运行时不拦，但 PyCharm 会标红
    except Exception as e:      # noqa: BLE001
        print(e)
    print("  >> pair(1, 'x') 运行时照样输出 (1, 'x')，只有静态检查器会报错——这正说明注解是"渐进"的。")


# ================= 5.5 泛型类 =================

class Stack(Generic[T]):
    """经典写法：继承 Generic[T]。"""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> Self:
        self._items.append(item)
        return self

    def pop(self) -> T:
        return self._items.pop()

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items!r})"


class Box[U]:        # PEP 695 新写法（3.12+），不用继承 Generic
    def __init__(self, item: U) -> None:
        self.item = item

    def map[V](self, fn: Callable[[U], V]) -> Box[V]:
        return Box(fn(self.item))

    def __repr__(self) -> str:
        return f"Box({self.item!r})"


def demo_5_generic_class() -> None:
    print("=" * 66)
    print("5.5 泛型类：Stack[int] 和 Stack[str] 是两种"检查器视角"下的类型")
    s: Stack[int] = Stack()
    s.push(1).push(2)
    print(f"  s = {s}, len = {len(s)}, pop = {s.pop()}")
    print(f"  b = Box(3).map(lambda x: str(x) * x) -> {Box(3).map(lambda x: str(x) * x)}")
    print("  >> s.push('a') 会被标红，因为 s 已声明为 Stack[int]。")


# ================= 5.6 TypedDict：给裸 dict 定结构 =================

class Student(TypedDict):
    name: str
    score: int


class DetailStudent(Student, total=False):
    """total=False 表示这一层的键全都可选。"""
    email: str
    city: str


def average(students: Sequence[Student]) -> float:
    return sum(s["score"] for s in students) / len(students)


def demo_6_typeddict() -> None:
    print("=" * 66)
    print("5.6 TypedDict —— 最适合你作业里那种 [{'name':..., 'score':...}] 数据")
    roster: list[Student] = [
        {"name": "张三", "score": 85},
        {"name": "李四", "score": 92},
        {"name": "王五", "score": 68},
    ]
    print(f"  roster[0] = {roster[0]}")
    print(f"  roster[0]['name'] 的静态类型是 str，PyCharm 补全会列出 name/score")
    print(f"  average(roster) = {average(roster):.2f}")
    print(f"  运行时 type(roster[0]) = {type(roster[0]).__name__}  <- 就是普通 dict，零开销")
    d: DetailStudent = {"name": "赵六", "score": 73, "city": "广州"}
    print(f"  DetailStudent(可选键) = {d}")
    print("  >> 写 {'name': 1} 或 s['scroe']（拼错）都会被标红，裸 dict 做不到这点。")


# ================= 5.7 NamedTuple 与 dataclass =================

class Point(NamedTuple):
    x: int
    y: int
    label: str = ""


@dataclass(slots=True)
class Course:
    title: str
    credit: float
    students: list[Student] = field(default_factory=list)   # 可变字段必须用 default_factory

    def add(self, student: Student) -> Self:
        self.students.append(student)
        return self

    @property
    def average(self) -> float:
        return average(self.students) if self.students else 0.0


def demo_7_structured() -> None:
    print("=" * 66)
    print("5.7 TypedDict / NamedTuple / dataclass 怎么选")
    p = Point(1, 2, "原点")
    print(f"  NamedTuple: {p}, p.x = {p.x}, 解包 = {tuple(p)}, 不可变 = 无 __setattr__")

    c = Course("软件工程", 3.0)
    c.add({"name": "张三", "score": 85}).add({"name": "李四", "score": 92})
    print(f"  dataclass : {c}")
    print(f"  自动生成的 __eq__ -> {Course('a', 1.0) == Course('a', 1.0)}")
    print("""  选择指南：
    数据来自 JSON / 外部 API，想保持 dict 形态 -> TypedDict
    需要不可变、可解包、能当 dict key        -> NamedTuple
    需要方法、默认值、可变、slots 省内存      -> dataclass""")


# ================= 5.8 overload / NoReturn / assert_never / cast =================

@overload
def repeat(value: str, times: int) -> str: ...
@overload
def repeat(value: list[Any], times: int) -> list[Any]: ...
def repeat(value: str | list[Any], times: int) -> str | list[Any]:
    """实现体只有一个，overload 只是给检查器看的"多张签名牌"。"""
    return value * times


def fail(msg: str) -> NoReturn:
    """NoReturn：函数一定不正常返回（raise / sys.exit / 死循环）。"""
    raise RuntimeError(msg)


def grade_of(level: Literal["low", "mid", "high"]) -> str:
    match level:
        case "low":
            return "初级"
        case "mid":
            return "中级"
        case "high":
            return "高级"
        case _ as unreachable:
            return assert_never(unreachable)   # 将来有人加了 "expert" 却忘了改这里，检查器立刻报错


def demo_8_advanced() -> None:
    print("=" * 66)
    print("5.8 overload / NoReturn / assert_never / cast")
    print(f"  repeat('ab', 3)     -> {repeat('ab', 3)!r}    检查器知道结果是 str")
    print(f"  repeat([1, 2], 2)   -> {repeat([1, 2], 2)}  检查器知道结果是 list")
    print(f"  grade_of('mid')     -> {grade_of('mid')}")
    try:
        fail("boom")
    except RuntimeError as e:
        print(f"  fail('boom')        -> RuntimeError: {e}")

    raw: Any = json.loads('{"score": 85}')
    data = cast(dict[str, int], raw)   # 运行时 cast 原样返回，零成本
    print(f"  cast(dict[str,int], json.loads(...)) -> {data}, 类型 {type(data).__name__}")
    print("  >> cast 是"我比检查器更懂"的承诺书，写错了它不救你；能不用就不用。")


if __name__ == "__main__":
    demo_1_basic()
    demo_2_containers()
    demo_3_callable()
    demo_4_typevar()
    demo_5_generic_class()
    demo_6_typeddict()
    demo_7_structured()
    demo_8_advanced()
    print("=" * 66)
    print("本讲速查表见文件末尾注释。")

# ------------------------------------------------------------------
# typing 速查表（Python 3.13）
# ------------------------------------------------------------------
# 联合/可选      int | None          Optional[int]     int | str
# 字面量         Literal["A", "B"]
# 常量           Final / Final[int]
# 别名           type X = list[int]  （3.12+）
# 语义新类型     UserId = NewType("UserId", int)
# 容器           list[int] dict[str,int] tuple[int,...] tuple[str,int] set[str]
# 抽象容器       Iterable[T] Sequence[T] Mapping[K,V] Iterator[T]
#                Generator[YieldT, SendT, ReturnT]
# 函数           Callable[[int, str], bool]   Callable[..., Any]
# 泛型           def f[T](x: T) -> T          class C[T]:        （3.12+）
#                T = TypeVar("T"); Generic[T]                     （经典）
#                TypeVar("T", bound=Sequence)  TypeVar("T", int, float)
# dict 结构      class P(TypedDict): name: str  /  NotRequired / total=False
# 类             @dataclass  /  NamedTuple
# 其它           overload  NoReturn  Never  assert_never  Self  cast  Any  object
# ------------------------------------------------------------------










    """
第 6 讲 综合实战：把 1~5 讲全部用起来，重构你作业里的"学生成绩"场景
后半部分是 8 道练习题，答案在文件末尾注释里（先自己写，再看答案）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Self,
    Sequence,
    TypedDict,
)

# ---------- 类型定义层 ----------

Grade = Literal["A", "B", "C", "D", "F"]
SortKey = Callable[["Student"], Any]


class Student(TypedDict):
    """对应你作业里的 {"name": "张三", "score": 85}，但现在有了结构约束。"""
    name: str
    score: int


class HasScore(Protocol := None) if False else object:  # 占位，见下方真实定义
    pass


# 用 Protocol 做"结构类型"：任何带 score 属性的对象都能被排序
from typing import Protocol  # noqa: E402


@runtime_checkable_if_needed
def _noop() -> None:
    pass


def runtime_checkable_if_needed(f: Any) -> Any:   # 仅为让上面占位可运行的兼容 shim
    return f


class Scored(Protocol):
    score: int


# ---------- 业务逻辑层 ----------

def to_grade(score: int) -> Grade:
    """Literal + if 链：返回值被限制在 5 个字面量之内。"""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def word_count(text: str) -> dict[str, int]:
    """重写你 work.py 里的 word_count：用 join 代替 += 拼接，用 dict.get 累加代替 O(n²) 的 count。"""
    kept: list[str] = [ch for ch in text.lower() if ch.isalpha() or ch.isspace() or ch == "'"]
    words: list[str] = "".join(kept).split()
    result: dict[str, int] = {}
    for w in words:
        result[w] = result.get(w, 0) + 1
    return result


def top_n_counts(counter: Mapping[str, int], n: int) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda kv: kv[1], reverse=True)[:n]


from typing import Mapping  # noqa: E402


class Repository[T]:
    """泛型仓库：既能装 Student(dict)，也能装 dataclass，还能像序列一样用（鸭子类型）。"""

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._items: list[T] = list(items)

    def add(self, item: T) -> Self:
        self._items.append(item)
        return self

    def extend(self, items: Iterable[T]) -> Self:
        self._items.extend(items)
        return self

    def filter(self, predicate: Callable[[T], bool]) -> Repository[T]:
        return Repository(x for x in self._items if predicate(x))

    def sorted_by(self, key: Callable[[T], Any], reverse: bool = False) -> list[T]:
        return sorted(self._items, key=key, reverse=reverse)

    def group_by(self, key: Callable[[T], Any]) -> dict[Any, list[T]]:
        groups: dict[Any, list[T]] = {}
        for item in self._items:
            groups.setdefault(key(item), []).append(item)
        return groups

    # --- 协议方法：让它"看起来像"一个只读序列 ---
    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __repr__(self) -> str:
        return f"Repository({self._items!r})"


@dataclass(slots=True)
class Course:
    title: str
    credit: float
    students: Repository[Student] = field(default_factory=Repository)

    def enroll(self, student: Student) -> Self:
        self.students.add(student)
        return self

    @property
    def average(self) -> float:
        return sum(s["score"] for s in self.students) / len(self.students) if len(self.students) else 0.0

    def report(self) -> str:
        lines = [f"《{self.title}》 学分 {self.credit} 人数 {len(self.students)} 平均分 {self.average:.2f}"]
        for rank, s in enumerate(self.students.sorted_by(lambda x: x["score"], reverse=True), start=1):
            lines.append(f"  第{rank}名：{s['name']} {s['score']}分 等级 {to_grade(s['score'])}")
        return "\n".join(lines)


# ---------- 演示 ----------

def main() -> None:
    raw: list[Student] = [
        {"name": "张三", "score": 85},
        {"name": "李四", "score": 92},
        {"name": "王五", "score": 68},
        {"name": "赵六", "score": 73},
        {"name": "孙七", "score": 55},
    ]

    course = Course("软件工程", 3.0)
    course.students.extend(raw)
    print(course.report())

    print("\n按等级分组：")
    for grade, members in course.students.group_by(lambda s: to_grade(s["score"])).items():
        print(f"  {grade}: {[m['name'] for m in members]}")

    print("\n及格的人：", course.students.filter(lambda s: s["score"] >= 60).sorted_by(lambda s: s["name"]))

    print("\n鸭子类型：Repository 能被所有接受可迭代对象的内置函数直接使用")
    print(f"  len = {len(course.students)}, max = {max(course.students, key=lambda s: s['score'])}")
    print(f"  list(...) 前两项 = {list(course.students)[:2]}")

    print("\n词频（改进版）：")
    text = "Hello world! hello, Python. world world?"
    counts = word_count(text)
    print(f"  {counts}")
    print(f"  top 2 -> {top_n_counts(counts, 2)}")


# ==================================================================
# 练习题（先自己写，写完再翻下面的答案）
# ==================================================================
#
# 练习 1  说出下面每行的输出，并解释原因：
#         a = [1, 2, 3]; b = a; b += [4]; print(a)
#         c = (1, 2, 3); d = c; d += (4,); print(c)
#
# 练习 2  说出输出：
#         def f(x, lst=[]):
#             lst.append(x); return lst
#         print(f(1), f(2), f(3, []), f(4))
#
# 练习 3  给下面函数补全最合适的注解（入参用抽象类型，返回用具体类型）：
#         def merge(a, b):        # a、b 是任意可迭代的同类型元素，返回新列表
#             return list(a) + list(b)
#
# 练习 4  用 Protocol 写一个 SupportsArea，让 Circle 和 Rect（无共同父类）
#         都能传给 print_area()。
#
# 练习 5  用 TypedDict 重构：
#         [{"title": "软件工程", "credit": 3.0, "teacher": "王老师"}, ...]
#         其中 teacher 是可选键。
#
# 练习 6  写一个泛型函数 second_last[T](seq) -> T，返回倒数第二个元素。
#         再想想：为什么不能写成 -> Any？
#
# 练习 7  下面代码会抛什么异常？抛出后 t 的值是什么？为什么？
#         t = ([1, 2],)
#         t[0] += [3]
#
# 练习 8  用 Literal + match 实现：
#         def cn_weekday(d: Literal[1,2,3,4,5,6,7]) -> str 返回"星期一"..."星期日"，
#         并用 assert_never 保证将来扩展字面量时检查器会提醒你。
#
# ==================================================================
# 参考答案
# ==================================================================
#
# 1  a -> [1, 2, 3, 4]（list 的 += 是 __iadd__ 原地扩展，b 和 a 是同一对象）
#    c -> (1, 2, 3)   （tuple 不可变，d += (4,) 是把名字 d 重绑到新 tuple，c 不受影响）
#
# 2  [1] [1, 2] [3] [1, 2, 4]
#    第三次传了显式 []，是全新列表所以只有 3；第四次又用回那个共享的默认列表。
#
# 3  from typing import TypeVar
#    T = TypeVar("T")
#    def merge(a: Iterable[T], b: Iterable[T]) -> list[T]:
#        return list(a) + list(b)
#    # 3.12+ 可写 def merge[T](a: Iterable[T], b: Iterable[T]) -> list[T]:
#
# 4  from typing import Protocol
#    class SupportsArea(Protocol):
#        def area(self) -> float: ...
#    class Circle:
#        def __init__(self, r: float) -> None: self.r = r
#        def area(self) -> float: return 3.14159 * self.r ** 2
#    class Rect:
#        def __init__(self, w: float, h: float) -> None: self.w, self.h = w, h
#        def area(self) -> float: return self.w * self.h
#    def print_area(shape: SupportsArea) -> None: print(shape.area())
#
# 5  from typing import NotRequired, TypedDict
#    class CourseInfo(TypedDict):
#        title: str
#        credit: float
#        teacher: NotRequired[str]
#
# 6  def second_last[T](seq: Sequence[T]) -> T: return seq[-2]
#    写 -> Any 的话，second_last([1,2,3]) 的结果在检查器眼里是 Any，
#    后续 result.upper() 这种错误不会被发现；用 TypeVar 才能把 str 一路传递下去。
#
# 7  TypeError: 'tuple' object does not support item assignment
#    但 t 变成了 ([1, 2, 3],)。因为 += 先执行 t[0].__iadd__([3])（原地修改成功），
#    再执行"把结果存回 t[0]"这一步才失败。异常抛了，副作用留下了。
#
# 8  from typing import Literal, assert_never, NoReturn
#    def cn_weekday(d: Literal[1,2,3,4,5,6,7]) -> str:
#        match d:
#            case 1: return "星期一"
#            case 2: return "星期二"
#            case 3: return "星期三"
#            case 4: return "星期四"
#            case 5: return "星期五"
#            case 6: return "星期六"
#            case 7: return "星期日"
#            case _ as unreachable: return assert_never(unreachable)
#
# ==================================================================


if __name__ == "__main__":
    main()


  """
   上面第 6 讲文件里我留了几行"占位/shim"代码（HasScore、_noop、runtime_checkable_if_needed 以及散落的 import），那是我为了演示 Protocol 定义顺序临时加的，你创建文件时请把它们全部删掉，只保留干净版本。为避免你手工删错，这里给出需要删除的行：
删掉 class HasScore(Protocol := None) if False else object: 到 pass 这一整块（含 Protocol := None 这种写法本身是语法错误，必须删）
删掉 from typing import Protocol # noqa: E402 上方那个 @runtime_checkable_if_needed 装饰的 def _noop() 整块
删掉 def runtime_checkable_if_needed(...) 整个函数
把 from typing import Mapping # noqa: E402 和 from typing import Protocol # noqa: E402 合并进文件顶部的主 from typing import (...) 里，加上 Mapping 和 Protocol
更简单的做法：直接把顶部导入块写成下面这样，然后删掉中间那些占位函数，Scored 这个 Protocol 类紧接在导入块之后定义即可：
  """

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    Protocol,
    Self,
    Sequence,
    TypedDict,
)

Grade = Literal["A", "B", "C", "D", "F"]
SortKey = Callable[["Student"], Any]

class Student(TypedDict):
    name: str
    score: int

class Scored(Protocol):
    score: int
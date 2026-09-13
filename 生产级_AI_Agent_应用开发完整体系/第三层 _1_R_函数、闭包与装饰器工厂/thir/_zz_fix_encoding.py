"""临时工具：把源码里 GBK 控制台无法输出的字符替换掉，并做编码自检。用完即删。"""
import pathlib
import sys

REPLACES: dict[str, str] = {
    "\u25b6": "\u2605",                       # ▶  -> ★（GBK 可输出）
    "\u2713": "[OK]",                        # ✓
    "\u2717": "[X]",                         # ✗
    "\u2192": "->",                          # →
    "\u2265": ">=",                          # ≥
    "\u2264": "<=",                          # ≤
    "\u00b7\u00b7": "--",                    # ··
}


def main() -> None:
    root = pathlib.Path(__file__).parent
    for p in sorted(root.glob("*.py")):
        if p.name == pathlib.Path(__file__).name:
            continue
        text = p.read_text(encoding="utf-8")
        new = text
        for old, rep in REPLACES.items():
            new = new.replace(old, rep)
        if new != text:
            p.write_text(new, encoding="utf-8")
            print("fixed:", p.name)
        # 编码自检：找出 GBK 控制台无法输出的字符
        bad = sorted({c for c in new if _cannot_gbk(c)})
        if bad:
            print("  GBK 不支持的字符:", [f"{c}(U+{ord(c):04X})" for c in bad])
    print("done")


def _cannot_gbk(ch: str) -> bool:
    try:
        ch.encode("gbk")
        return False
    except UnicodeEncodeError:
        return True


if __name__ == "__main__":
    sys.exit(main())

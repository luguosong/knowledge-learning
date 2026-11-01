#!/usr/bin/env python3
"""构建期反向链接生成器。

扫描 站点/docs 下文章间的站内相对链接，向每个被引用文章末尾追加
「引用本页的文章」小节。生成块带标记注释，重跑时先剥离旧块再生成（幂等）。
生成块不提交入库：CI 在 zensical build 前对检出副本运行本脚本。
本地预览同样先运行再构建，提交前用 git checkout -- 站点/docs 撤销生成块。

用法：python3 站点/工具/backlinks.py [--selftest]
"""
import os
import re
import sys
import tempfile
from pathlib import Path

MARK_START = "<!-- backlinks:start -->"
MARK_END = "<!-- backlinks:end -->"
SECTION_TITLE = "## 引用本页的文章"
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")
EXTERNAL = ("http://", "https://", "mailto:")


def strip_block(text: str) -> str:
    if MARK_START not in text:
        return text
    before = text.split(MARK_START, 1)[0].rstrip("\n")
    after = text.split(MARK_END, 1)[1].lstrip("\n") if MARK_END in text else ""
    return before + "\n\n" + after if after else before + "\n"


def h1_title(text: str, fallback: str) -> str:
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def rel_link(dst: Path, src: Path) -> str:
    return Path(os.path.relpath(src, dst.parent)).as_posix()


def run(root: Path) -> int:
    pages = {f.resolve(): f.read_text(encoding="utf-8") for f in sorted(root.rglob("*.md"))}
    stripped = {p: strip_block(t) for p, t in pages.items()}
    inbound = {p: [] for p in pages}
    for src, text in stripped.items():
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("#", 1)[0].strip()
            if not target or target.startswith(EXTERNAL):
                continue
            dst = (src.parent / target).resolve()
            if dst in stripped and dst != src:
                inbound[dst].append(src)
    changed = 0
    for p, body in stripped.items():
        refs = sorted(set(inbound[p]))
        had_block = MARK_START in pages[p]
        if refs:
            bullets = "\n".join(
                f"- [{h1_title(pages[s], s.stem)}]({rel_link(p, s)})" for s in refs
            )
            new_text = body.rstrip("\n") + f"\n\n{MARK_START}\n\n{SECTION_TITLE}\n\n{bullets}\n\n{MARK_END}\n"
            if new_text != pages[p]:
                p.write_text(new_text, encoding="utf-8")
                changed += 1
        elif had_block:
            p.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
            changed += 1
    return changed


def selftest() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "sub").mkdir()
        (root / "a.md").write_text("# A\n\n见 [B](b.md) 与 [外](https://x.test/)。\n", encoding="utf-8")
        (root / "b.md").write_text("# B\n\n见 [A](a.md)。\n", encoding="utf-8")
        (root / "sub/c.md").write_text("# C\n\n见 [B](../b.md)、[锚](../b.md#x) 与 ![图](img.png)。\n", encoding="utf-8")
        assert run(root) == 2, "应恰好改写 a.md 与 b.md"
        b = (root / "b.md").read_text(encoding="utf-8")
        assert "[A](a.md)" in b and "[C](sub/c.md)" in b, b
        assert MARK_START not in (root / "sub/c.md").read_text(encoding="utf-8"), "无人引用不得生成"
        snap = {f: f.read_text(encoding="utf-8") for f in root.rglob("*.md")}
        assert run(root) == 0, "重跑必须零改写"
        assert snap == {f: f.read_text(encoding="utf-8") for f in root.rglob("*.md")}, "幂等失败"
        (root / "b.md").write_text("# B\n\n无链接。\n", encoding="utf-8")
        run(root)
        assert MARK_START not in (root / "a.md").read_text(encoding="utf-8"), "引用消失应剥离生成块"
    print("selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        root = Path(__file__).resolve().parent.parent / "docs"
        print(f"backlinks: {run(root)} 个页面更新")

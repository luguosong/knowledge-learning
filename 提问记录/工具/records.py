"""提问记录的确定性检索与体检。Python 3.10+，仅使用标准库。"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from knowledge import Entry, field, load, read, scan, valid_date
from references import ReferenceIndex

ROOT = Path(__file__).resolve().parents[1]
PAGE_SIZE = 50
AUTO_NOTE = "> 自动生成；请编辑问题条目及领域综述。"
PAGE_FILE = re.compile(r"\d{3,}")


def generated_block(text: str, name: str, content: str) -> str:
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise ValueError(f"生成区 {name} 必须有一对标记")
    pattern = re.escape(start) + r".*?" + re.escape(end)
    return re.sub(pattern, lambda _: start + "\n" + content.rstrip() + "\n" + end, text, flags=re.S)


def expected(root: Path, index: str, domains: dict, entries: list[Entry]) -> dict[Path, str]:
    outputs = {}
    compatibility = json.loads(read(root / "管理" / "兼容链接.json"))
    by_id = {e.id: e for e in entries}
    by_domain = {d: [] for d in domains}
    for entry in entries:
        by_domain[entry.domain].append(entry)
    for values in by_domain.values():
        values.sort(key=lambda e: (e.created, e.id))
    for domain, (_, _, _) in domains.items():
        values = by_domain[domain]
        if not values:
            raise ValueError("领域没有条目: " + domain)
        last = max(e.updated for e in values)
        line = f"{domain} —— {domains[domain][0]} · {len(values)} 条 · 至 {last}"
        index = re.sub(r"^" + re.escape(domain) + r" —— .+$", lambda _: line, index, flags=re.M)
        hub_path = root / f"{domain}.md"
        hub = read(hub_path)
        pages = []
        for number, offset in enumerate(range(0, len(values), PAGE_SIZE), 1):
            group = values[offset:offset + PAGE_SIZE]
            page_path = root / "目录" / domain / f"{number:03}.md"
            pages.append(f"- [[目录/{domain}/{number:03}|第 {number} 页]]：{group[0].created} 至 {group[-1].created} · {len(group)} 条")
            lines = [f"# {domain} · 第 {number} 页", "", AUTO_NOTE, "", f"[[{domain}|领域综述]]", ""]
            if number > 1:
                lines += [f"[[目录/{domain}/{number-1:03}|上一页]]", ""]
            if offset + PAGE_SIZE < len(values):
                lines += [f"[[目录/{domain}/{number+1:03}|下一页]]", ""]
            lines += [f"- [[条目/{e.id}|{e.title}]] · 至 {e.updated}" for e in group]
            outputs[page_path] = "\n".join(lines) + "\n"
        hub = generated_block(hub, "catalog", "\n".join(pages))
        aliases = []
        for old in compatibility:
            if old["domain"] != domain:
                continue
            if old["id"] not in by_id:
                raise ValueError("兼容链接目标丢失: " + old["id"])
            aliases += [f'## {old["title"]}', "", f'正文：[[条目/{old["id"]}|{old["title"]}]]', ""]
        hub = generated_block(hub, "legacy", "\n".join(aliases))
        outputs[hub_path] = hub
    outputs[root / "索引.md"] = index
    return outputs


def owned_catalog_page(root: Path, path: Path) -> bool:
    """目录页归属判定：文件名序号、首行标题与生成声明一致；不一致视为未知文件。"""
    number = PAGE_FILE.fullmatch(path.stem)
    if not number or path.parent.parent != root / "目录":
        return False
    try:
        lines = read(path).splitlines()
    except (OSError, UnicodeDecodeError):
        return False
    return bool(lines) and lines[0] == f"# {path.parent.name} · 第 {int(number[0])} 页" and AUTO_NOTE in lines


def examine(root: Path):
    index, domains, entries, errors = load(root)
    outputs = {}
    if not errors:
        try:
            outputs = expected(root, index, domains, entries)
        except (ValueError, OSError, KeyError) as exc:
            errors.append(str(exc))
    return domains, entries, outputs, errors


def entry_text(root: Path, entry: Entry) -> str:
    appendix = root / "附录" / f"{entry.id}.md"
    return entry.body + ("\n" + read(appendix) if appendix.is_file() else "")


def atomic_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".records-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def writer_lock(root: Path):
    path = root / "管理" / ".records.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError("存在写入锁；确认其他维护进程已结束后再移除 管理/.records.lock")
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)


def command_check(root: Path, sync=False):
    domains, entries, outputs, errors = examine(root)
    warnings = []
    paths = [root / f"{domain}.md" for domain in domains] + [e.path for e in entries]
    appendix_paths = list((root / "附录").glob("*.md"))
    ids = {e.id for e in entries}
    for path in appendix_paths:
        if path.stem not in ids:
            errors.append("附录缺少所属问题: " + path.name)
    paths += appendix_paths
    known_hubs = {root / f"{domain}.md" for domain in domains} | {root / "索引.md"}
    errors += ["未登记的领域文件: " + p.name for p in root.glob("*.md") if p not in known_hubs]
    documents = {p.resolve(): read(p) for p in paths if p.exists()}
    # sync 校验将要生成的内容；普通 check 校验磁盘实物。
    if sync:
        documents.update({p.resolve(): t for p, t in outputs.items()})
    else:
        for path in (root / "目录").rglob("*.md"):
            documents[path.resolve()] = read(path)
    references = ReferenceIndex(root, documents, {e.id: e.path for e in entries}, json.loads(read(root / "管理" / "兼容链接.json")))
    errors += references.errors()
    by_id = {e.id: e for e in entries}
    for path in appendix_paths:
        if path.stem in by_id and not references.links_to(by_id[path.stem].path, path):
            errors.append("问题缺少附录入口: " + path.name)
    for domain in domains:
        path = root / f"{domain}.md"
        if not path.exists():
            errors.append("缺少领域文件: " + domain)
            continue
        text = read(path)
        match = re.search(r"^## 综述\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if not match or not match[1].strip():
            errors.append("缺少综述: " + domain)
        elif len(match[1].strip()) > 600:
            warnings.append(f"{domain}: 综述超过 600 字符")
    for entry in entries:
        if len(entry.body) > 12000:
            warnings.append(entry.id + ": 正文超过 12000 字符，按标题读取；需要时拆附录")
        verified = field(entry.body, "核实")
        for value in verified:
            if not valid_date(value[:10]):
                errors.append(entry.id + ": 核实字段须以日期开头")
    actual_catalogs = set((root / "目录").rglob("*.md"))
    stale = sorted(actual_catalogs - set(outputs)) if outputs else []
    owned = [path for path in stale if owned_catalog_page(root, path)]
    errors += [f"未知文件（需人工处理）: {path.relative_to(root)}" for path in stale if path not in owned]
    if not sync:
        errors += [f"过期目录页（运行 sync 将自动退役）: {path.relative_to(root)}" for path in owned]
    changes = {p: t for p, t in outputs.items() if not p.exists() or read(p) != t}
    if not sync:
        errors += ["派生内容未同步: " + str(p.relative_to(root)) for p in changes]
    retired = 0
    if sync and not errors:
        for path, content in changes.items():
            atomic_write(path, content)
        # 先写后退役：磁盘链接保持一致，中断后重跑 sync 收敛。
        for path in owned:
            path.unlink()
            print("退役：" + path.relative_to(root).as_posix())
        retired = len(owned)
        catalogs = root / "目录"
        if catalogs.is_dir():
            for folder in sorted(catalogs.iterdir()):
                if folder.is_dir() and not any(folder.iterdir()):
                    folder.rmdir()
    for message in errors:
        print("ERROR " + message)
    for message in warnings:
        print("WARN " + message)
    print(f"{len(domains)} 个领域，{len(entries)} 个问题；{len(errors)} 个错误，{len(warnings)} 个提示" + (f"；同步 {len(changes) if not errors else 0} 个文件，退役 {retired} 页" if sync else ""))
    return 1 if errors else 0


def command_find(root: Path, query: str, domain: str | None, limit: int):
    entries, known, findings = scan(root, domain)
    if domain and domain not in known:
        raise ValueError("领域未登记: " + domain)
    words = query.casefold().split()
    hits = []
    for entry in entries:
        title = entry.title.casefold()
        content = entry_text(root, entry).casefold()
        if all(w in title or w in content for w in words):
            score = sum(3 if w in title else 1 for w in words)
            hits.append((-score, entry.created, entry))
    for _, _, entry in sorted(hits, key=lambda h: (h[0], h[1], h[2].id))[:limit]:
        print(f"{entry.path.relative_to(root)} | {entry.domain} | {entry.title} | 至 {entry.updated}")
    print(f"命中 {len(hits)} 条，显示至多 {limit} 条")
    for finding in findings:
        print(f"DIAG {finding.scope} · {finding.message}")


def command_backlinks(root: Path, ident: str):
    entries, _, findings = scan(root)
    broken = {finding.path.stem for finding in findings if finding.path is not None}
    ids = {e.id for e in entries}
    if ident in broken:
        raise ValueError("目标条目无法解析: " + ident)
    if ident not in ids:
        raise ValueError("条目不存在或结构有错: " + ident)
    paths = [entry.path for entry in entries] + list((root / "附录").glob("*.md"))
    references = ReferenceIndex(root, {path: read(path) for path in paths}, {e.id: e.path for e in entries}, json.loads(read(root / "管理" / "兼容链接.json")))
    sources = references.incoming(ident)
    hits = [entry for entry in entries if entry.id in sources]
    for entry in hits:
        print(f"{entry.path.relative_to(root)} | {entry.domain} | {entry.title}")
    print(f"{len(hits)} 个问题引用此条目（不计自引用、目录及兼容入口）")
    for finding in findings:
        print(f"DIAG {finding.scope} · {finding.message}")
    if findings:
        print(f"DIAG 未归属 · {len(findings)} 条未解析，入链可能不全")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="提问记录目录；主要用于隔离验证")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="离线结构检查；不修改文件或核实网页事实")
    commands.add_parser("sync", help="更新目录、兼容入口及索引统计；保留人工综述与领域范围")
    search = commands.add_parser("find", help="标题优先检索，只输出候选条目")
    search.add_argument("query")
    search.add_argument("--domain")
    search.add_argument("--limit", type=int, default=10)
    backlinks = commands.add_parser("backlinks", help="反向检索问题间引用")
    backlinks.add_argument("id")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "sync":
            with writer_lock(root):
                return command_check(root, sync=True)
        if args.command == "check":
            return command_check(root)
        if args.command == "find":
            if args.limit < 1:
                raise ValueError("limit 必须大于 0")
            command_find(root, args.query, args.domain, args.limit)
        else:
            command_backlinks(root, args.id)
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print("ERROR " + str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())

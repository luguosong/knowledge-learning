#!/usr/bin/env python3
"""文章知识库：检索、关联、同步、校验和迁移验收。"""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import sys

from knowledge import ID, field, load, valid_date
from references import heading_positions, references, section, slug, visible


ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def writer_lock(root):
    path = root / "管理/.records.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stream = path.open("x")
    except FileExistsError:
        raise ValueError("存在写入锁: " + str(path)) from None
    try:
        with stream:
            yield
    finally:
        path.unlink()


def examine(root):
    documents, questions, domains, aliases, errors = load(root)
    if not documents:
        errors.append("站点没有文章")
    seen = set()
    for q in questions:
        location = f"{q.path.relative_to(root)}#{q.id}"
        if q.id in seen:
            errors.append(location + ": 问题 ID 重复")
        seen.add(q.id)
        if not valid_date(q.created) or q.id[2:10] != q.created.replace("-", ""):
            errors.append(location + ": 首次日期与 ID 不符")
        if not valid_date(q.updated) or q.updated < q.created:
            errors.append(location + ": 更新日期无效")
        if q.domain not in domains:
            errors.append(location + ": 领域未登记")
        if not re.search(r"\]\([^)]+\)", q.targets):
            errors.append(location + ": 缺少正文链接")
        targets = list(references(root, documents, {q.path: q.targets}))
        if not targets or any(ref.error or not section(documents.get(ref.path, ""), ref.anchor).strip() for ref in targets):
            errors.append(location + ": 正文入口必须定位知识章节，不能指向提问记录")
        allowed = {"原题", "问", "领域", "首次", "更新", "正文", "关联", "追问"}
        for line in q.text.splitlines():
            if not line.strip() or line.startswith(("  ", "\t")):
                continue
            match = re.match(r"^- \*\*([^*]+)\*\*：", line)
            if not match or match[1] not in allowed:
                errors.append(location + ": 提问记录只允许追溯字段，不能保存答案或推导")
                break
    for name, entries in domains.items():
        if len(entries) != 1:
            errors.append("领域范围重复: " + name)
        for path, block in entries:
            if not field(block, "范围") or not field(block, "综述"):
                errors.append(f"{path.relative_to(root)}: 领域范围或综述缺失 {name}")
    for path, text in documents.items():
        prose = visible(text)
        if len(re.findall(r"^# ", prose, re.M)) != 1:
            errors.append(f"{path.relative_to(root)}: 必须只有一个一级标题")
        if "[[" in prose:
            errors.append(f"{path.relative_to(root)}: 旧 wiki 链接未转换")
        if len(re.findall(r"^### q-", prose, re.M)) != sum(q.path == path for q in questions):
            errors.append(f"{path.relative_to(root)}: 提问记录身份或字段无效")
    for item in aliases:
        if item["id"] not in seen:
            errors.append("兼容映射目标缺失: " + item["id"])
    for ref in references(root, documents):
        if ref.error:
            errors.append(f"{ref.source.relative_to(root)}: {ref.error} {ref.raw}")
    data = {
        "domains": {name: {"path": entries[0][0].relative_to(root).as_posix(),
                           "scope": field(entries[0][1], "范围")}
                    for name, entries in sorted(domains.items())},
        "questions": [{"id": q.id, "path": q.path.relative_to(root).as_posix(), "title": q.title,
                       "domain": q.domain, "created": q.created, "updated": q.updated}
                      for q in sorted(questions, key=lambda q: q.id)],
    }
    return data, errors


def command_check(root, sync=False):
    data, errors = examine(root)
    path = root / "管理/索引.json"
    expected = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if not errors:
        if sync:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".tmp")
            temporary.write_text(expected, encoding="utf-8")
            temporary.replace(path)
        elif not path.exists() or path.read_text(encoding="utf-8") != expected:
            errors.append("索引过期，请运行 sync")
    for error in errors:
        print("ERROR " + error)
    print(f"{len(data['domains'])} 个领域，{len(data['questions'])} 个问题；{len(errors)} 个错误")
    return int(bool(errors))


def command_find(root, query, domain, limit):
    documents, questions, domains, aliases, errors = load(root)
    if domain and domain not in domains:
        raise ValueError("领域未登记: " + domain)
    hits = []
    words = query.casefold().split()
    for question in questions:
        if domain and question.domain != domain:
            continue
        if ID.fullmatch(query) and question.id != query:
            continue
        names = " ".join(a["title"] for a in aliases if a["id"] == question.id)
        title = f"{question.id} {question.title} {question.query} {field(question.text, '追问')} {names}".casefold()
        targets = list(references(root, documents, {question.path: question.targets}))
        snippets = [(ref, section(documents.get(ref.path, ""), ref.anchor).casefold())
                    for ref in targets if not ref.error]
        body = "\n".join(text for _, text in snippets)
        if all(w in title or w in body for w in words):
            target = max(snippets, key=lambda item: sum(w in item[1] for w in words), default=(None, ""))[0]
            location = (target.path if target else question.path).relative_to(root).as_posix()
            if target and not target.anchor:
                text = documents.get(target.path, "").partition("\n## 提问记录\n")[0]
                positions = [text.casefold().find(w) for w in words if w in text.casefold()]
                if positions:
                    candidates = [title for start, _, title in heading_positions(text) if start <= min(positions)]
                    if candidates:
                        location += "#" + slug(candidates[-1])
            if target and target.anchor:
                location += "#" + target.anchor
            elif target is None:
                location += "#" + question.id
            hits.append((-sum(3 if w in title else 1 for w in words), question.id, location, question))
    for _, _, location, q in sorted(hits)[:limit]:
        print(f"{location} | {q.id} | {q.domain} | {q.title} | 至 {q.updated}")
    print(f"命中 {len(hits)} 条，显示至多 {limit} 条")
    for error in errors:
        print("DIAG " + error)


def command_backlinks(root, target):
    documents, questions, _, _, errors = load(root)
    question = next((q for q in questions if q.id == target), None)
    if ID.fullmatch(target):
        if question is None:
            raise ValueError("问题不存在或结构有错: " + target)
        path, anchor = question.path, question.id
    else:
        file, _, anchor = target.partition("#")
        path = (root / file).resolve()
        if path not in documents:
            raise ValueError("文章不存在: " + target)
    hits = {ref.source for ref in references(root, documents)
            if not ref.error and ref.path == path and ref.source != path
            and (not anchor or ref.anchor == anchor)}
    for source in sorted(hits):
        print(source.relative_to(root).as_posix())
    print(f"{len(hits)} 篇文章引用此目标（不计自引用、重复链接）")
    for error in errors:
        print("DIAG " + error)


def command_audit(root):
    documents, questions, _, _, errors = load(root)
    manifest = json.loads((root / "管理/迁移核对.json").read_text(encoding="utf-8"))
    by_id = {q.id: q for q in questions}
    for old in manifest["questions"]:
        q = by_id.get(old["id"])
        if q is None:
            errors.append("原问题丢失: " + old["id"])
            continue
        for name in ["created", "updated", "title", "domain", "query"]:
            if getattr(q, name) != old[name]:
                errors.append(f"{q.id}: 迁移改变了 {name}")
        text = documents[q.path]
        for url in old.get("sources", []):
            if url not in text:
                errors.append(f"{q.id}: 原来源未保留 {url}")
    for item in manifest["attachments"]:
        path = (root / item["path"]).resolve()
        if not path.is_relative_to(root / "docs") or not path.is_file():
            errors.append("附件缺失: " + item["path"])
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            errors.append("附件哈希不符: " + item["path"])
    for error in errors:
        print("ERROR " + error)
    print(f"迁移核对 {len(manifest['questions'])} 个问题、{len(manifest['attachments'])} 个附件；{len(errors)} 个错误")
    return int(bool(errors))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="站点根目录；可用于隔离验证")
    commands = parser.add_subparsers(dest="command", required=True)
    search = commands.add_parser("find", help="按主题、原问题或旧标题返回文章章节")
    search.add_argument("query")
    search.add_argument("--domain")
    search.add_argument("--limit", type=int, default=10)
    commands.add_parser("sync", help="校验后生成索引，不改写文章正文")
    commands.add_parser("check", help="只读检查身份、日期、链接与索引")
    commands.add_parser("audit", help="按迁移清单核对原问题日期、来源与附件哈希；仅供迁移验收")
    backlinks = commands.add_parser("backlinks", help="查询指向问题 ID 或文章章节的入链")
    backlinks.add_argument("target")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if args.command == "sync":
            with writer_lock(root):
                return command_check(root, sync=True)
        if args.command == "check":
            return command_check(root)
        if args.command == "audit":
            return command_audit(root)
        if args.command == "backlinks":
            command_backlinks(root, args.target)
            return 0
        if args.limit < 1:
            raise ValueError("limit 必须大于 0")
        command_find(root, args.query, args.domain, args.limit)
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print("ERROR " + str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())

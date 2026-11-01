"""知识库：问题条目的发现、解析、范围与诊断。查询与体检共用，不在各命令中分别推断。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re

from references import visible

ROW = re.compile(r"^(.+?) —— (.+?) · (\d+) 条 · 至 (\d{4}-\d{2}-\d{2})$")
ID = re.compile(r"q-\d{8}-\d{3,}")
HEADER = re.compile(r'---\nid: (q-\d{8}-\d{3,})\ndomain: ("[^\n]+")\n---\n\n# (\d{4}-\d{2}-\d{2}) · ([^\n]+)\n')
ENTRY = re.compile(HEADER.pattern + r"(.*)", re.S)
DOMAIN = re.compile(r'^domain: ("[^\n]+")$', re.M)
UNATTRIBUTED = "未归属"
LOCAL = "本领域"
FOREIGN = "其他领域"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def field(text: str, name: str) -> list[str]:
    return re.findall(r"^- \*\*" + re.escape(name) + r"\*\*：(.*?)(?=^- \*\*[^*\n]+\*\*：|^#{1,6} |\Z)", visible(text), re.M | re.S)


def valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    except ValueError:
        return False


def safe_name(value: str) -> bool:
    return bool(value.strip()) and not re.search(r'[<>:"/\\|?*\x00-\x1f]', value) and value not in {".", ".."} and not value.endswith((".", " "))


@dataclass
class Entry:
    path: Path
    id: str
    domain: str
    title: str
    created: str
    updated: str
    body: str


@dataclass
class Finding:
    scope: str
    message: str
    path: Path | None = None


def _validated_domain(path: Path, ident: str, domain_json: str, created: str) -> str:
    domain = json.loads(domain_json)
    if ident != path.stem:
        raise ValueError(f"{path.name}: 文件名与 id 不符")
    if not valid_date(created) or ident[2:10] != created.replace("-", ""):
        raise ValueError(f"{path.name}: 首次记录日期与 id 不符")
    return domain


def parse_entry(path: Path) -> Entry:
    text = read(path)
    m = ENTRY.fullmatch(text)
    if not m:
        raise ValueError(f"{path.name}: 条目格式不符")
    ident, domain_json, created, subject, body = m.groups()
    domain = _validated_domain(path, ident, domain_json, created)
    updates = field(body, "更新")
    dates = [created]
    for update in updates:
        value = update[:10]
        if not valid_date(value) or value < created:
            raise ValueError(f"{path.name}: 更新日期无效")
        dates.append(value)
    return Entry(path, ident, domain, f"{created} · {subject}", created, max(dates), body)


def open_header(path: Path) -> str:
    """只读条目头部（frontmatter 与标题行），供领域归属判定。"""
    lines: list[str] = []
    closed = 0
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            lines.append(line)
            if line.rstrip("\r\n") == "---":
                closed += 1
            elif closed >= 2 and line.startswith("# "):
                break
            if len(lines) >= 12:
                break
    return "".join(lines)


def classify(path: Path) -> tuple[str | None, str | None]:
    """只读头部，判定领域归属。返回 (领域, 错误信息)；健康头部错误信息为 None。"""
    domain = None
    try:
        header = open_header(path)
        found = DOMAIN.search(header)
        if found:
            try:
                domain = json.loads(found[1])
            except ValueError:
                pass
        match = HEADER.fullmatch(header)
        if not match:
            raise ValueError(f"{path.name}: 条目格式不符")
        ident, domain_json, created, _subject = match.groups()
        return _validated_domain(path, ident, domain_json, created), None
    except (OSError, ValueError) as exc:
        return domain, f"{path.name}: 无法读取" if isinstance(exc, OSError) else str(exc)


def scan(root: Path, domain: str | None = None) -> tuple[list[Entry], set[str], list[Finding]]:
    """按范围发现并解析问题条目；不读索引。

    domain 为 None 时全文解析所有条目，失败按“未归属”诊断；
    指定 domain 时其余条目只读头部，仅目标领域全文解析。
    返回 (可解析条目, 头部可判定的领域集, 诊断)。
    """
    entries: list[Entry] = []
    known: set[str] = set()
    findings: list[Finding] = []
    for path in sorted((root / "条目").glob("*.md")):
        if domain is None:
            try:
                entries.append(parse_entry(path))
            except (OSError, ValueError) as exc:
                findings.append(Finding(UNATTRIBUTED, str(exc), path))
            continue
        entry_domain, error = classify(path)
        if entry_domain is not None:
            known.add(entry_domain)
        if error is not None:
            scope = UNATTRIBUTED if entry_domain is None else (LOCAL if entry_domain == domain else FOREIGN)
            findings.append(Finding(scope, error, path))
            continue
        if entry_domain != domain:
            continue
        try:
            entries.append(parse_entry(path))
        except (OSError, ValueError) as exc:
            findings.append(Finding(LOCAL, str(exc), path))
    return entries, known, findings


def load(root: Path):
    """全库解析并收集体检错误；check 与 sync 依赖此口径，任一错误即失败。"""
    errors = []
    domains = {}
    index = read(root / "索引.md")
    for line in index.splitlines():
        match = ROW.fullmatch(line)
        if not match:
            if " —— " in line:
                errors.append("索引行格式不符: " + line)
            continue
        domain, scope, count, updated = match.groups()
        if domain in domains:
            errors.append("领域重复: " + domain)
        if not safe_name(domain):
            errors.append("领域名称不能用作文件名: " + domain)
        domains[domain] = (scope, int(count), updated)
    if not domains:
        errors.append("索引没有领域")
    entries = []
    titles = set()
    for path in sorted((root / "条目").glob("*.md")):
        try:
            entry = parse_entry(path)
            entries.append(entry)
            if entry.domain not in domains:
                errors.append(f"{path.name}: 领域未登记")
            key = (entry.domain, entry.title)
            if key in titles:
                errors.append(f"{path.name}: 同领域标题重复")
            titles.add(key)
            for name in ["问", "答", "信源"]:
                if not any(v.strip() for v in field(entry.body, name)):
                    errors.append(f"{path.name}: 缺少{name}")
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    return index, domains, entries, errors

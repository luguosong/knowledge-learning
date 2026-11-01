"""从唯一的文章正文读取范围与提问记录。"""
from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re


ID = re.compile(r"q-\d{8}-\d{3,}")
QUESTION = re.compile(r"^### (q-\d{8}-\d{3,})\s*$", re.M)
DOMAIN = re.compile(r"<!-- domain: (.+?) -->\n(.*?)<!-- /domain -->", re.S)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def field(text: str, name: str) -> str:
    match = re.search(
        r"^(?:- )?\*\*" + re.escape(name) + r"\*\*：(.*?)(?=^(?:- )?\*\*[^*\n]+\*\*：|^#{1,6} |\Z)",
        text, re.M | re.S,
    )
    return match[1].strip() if match else ""


def valid_date(value: str) -> bool:
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


@dataclass
class Question:
    id: str
    path: Path
    title: str
    domain: str
    created: str
    updated: str
    query: str
    targets: str
    text: str


def load(root: Path):
    documents = {p: read(p) for p in sorted((root / "docs").rglob("*.md"))}
    questions = []
    domains: dict[str, list[tuple[Path, str]]] = {}
    errors = []
    for path, text in documents.items():
        for match in DOMAIN.finditer(text):
            domains.setdefault(match[1], []).append((path, match[2].strip()))
        history = text.partition("\n## 提问记录\n")[2]
        matches = list(QUESTION.finditer(history))
        for i, match in enumerate(matches):
            block = history[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(history)].strip()
            values = [field(block, n) for n in ["原题", "领域", "首次", "更新", "问", "正文"]]
            if not all(values):
                errors.append(f"{path.relative_to(root)}#{match[1]}: 提问记录字段不全")
                continue
            title, domain, created, updated, query, targets = values
            questions.append(Question(match[1], path, title, domain, created, updated, query, targets, block))
    compatibility = root / "管理/兼容链接.json"
    aliases = json.loads(read(compatibility)) if compatibility.exists() else []
    return documents, questions, domains, aliases, errors

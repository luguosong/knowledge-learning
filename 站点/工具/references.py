"""标准 Markdown 链接的共同解释，供校验、查询与反向链接生成使用。"""
from dataclasses import dataclass
from html import unescape
from pathlib import Path
import re
from urllib.parse import unquote


def visible(text: str) -> str:
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            if fence is None:
                fence = match[1]
            elif match[1][0] == fence[0] and len(match[1]) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(re.sub(r"(`+).*?\1", lambda m: " " * len(m[0]), line))
    return "\n".join(lines)


def slug(title: str) -> str:
    plain = re.sub(r"[`*~]", "", title).strip().casefold()
    return re.sub(r"[\s-]+", "-", re.sub(r"[^\w\-\s]", "", plain)).strip("-")


def heading_positions(text: str):
    """标题的原文位置；围栏内的示例标题不参与导航。"""
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            if fence is None:
                fence = match[1]
            elif match[1][0] == fence[0] and len(match[1]) >= len(fence):
                fence = None
            offset += len(line)
            continue
        title = re.match(r"^(#{1,6}) (.+)$", line.rstrip("\r\n")) if fence is None else None
        if title:
            yield offset, len(title[1]), title[2]
        offset += len(line)


def headings(text: str) -> set[str]:
    anchors = set(re.findall(r'<a\s+id=["\']([^"\']+)["\']', text))
    counts: dict[str, int] = {}
    for _, _, title in heading_positions(text):
        base = slug(title)
        n = counts.get(base, 0)
        counts[base] = n + 1
        anchors.add(base + (f"_{n}" if n else ""))
    return anchors


def section(text: str, anchor: str) -> str:
    """读取一个章节，含其子章节，不包含提问记录。"""
    text = text.partition("\n## 提问记录\n")[0]
    if not anchor:
        return text
    matches = list(heading_positions(text))
    counts: dict[str, int] = {}
    for i, (start, level, title) in enumerate(matches):
        base = slug(title)
        n = counts.get(base, 0)
        counts[base] = n + 1
        if base + (f"_{n}" if n else "") != anchor:
            continue
        end = next((m[0] for m in matches[i + 1:] if m[1] <= level), len(text))
        return text[start:end]
    return ""


LINK = re.compile(
    r'''!?\[(?:\\.|[^\]\\\n])*\]\(\s*'''
    r'''(<[^>\n]+>|(?:\\.|[^\s()\\]|\([^()\n]*\))+?)'''
    r'''(?:[ \t]+(?:"[^"\n]*"|'[^'\n]*'|\([^()\n]*\)))?[ \t]*\)'''
)


@dataclass
class Reference:
    source: Path
    path: Path
    anchor: str
    raw: str
    error: str = ""


def references(root: Path, documents: dict[Path, str], sources=None):
    anchors = {p: headings(text) for p, text in documents.items()}
    for source, text in (documents if sources is None else sources).items():
        for match in LINK.finditer(visible(text)):
            target = unescape(match[1].strip("<>"))
            if re.match(r"(?:[a-zA-Z][\w+.-]*:|//)", target):
                continue
            file, _, anchor = unquote(target).partition("#")
            path = (source.parent / file).resolve() if file else source
            error = ""
            if not path.is_relative_to(root / "docs") or not path.is_file():
                error = "无效链接"
            elif anchor and path.suffix == ".md" and anchor not in anchors.get(path, set()):
                error = "无效标题"
            yield Reference(source, path, anchor, match[0], error)

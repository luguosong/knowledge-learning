"""本地链接的共同解释：校验、附录入口与问题入链使用相同身份。"""
from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from pathlib import Path
import re
from urllib.parse import unquote


def visible(text: str, *, inline: bool = True) -> str:
    """排除代码示例，保留正文链接所在的真实文档位置。"""
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
            lines.append(re.sub(r"(`+).*?\1", "", line) if inline else line)
    return "\n".join(lines)


_WIKI = re.compile(r"\[\[([^\]\n]+)\]\]")
_MARKDOWN = re.compile(
    r'''(?<!!)\[(?:\\.|[^\]\\\n])*\]\(\s*'''
    r'''(<[^>\n]+>|(?:\\.|[^\s()\\]|\([^()\n]*\))+?)'''
    r'''(?:[ \t]+(?:"[^"\n]*"|'[^'\n]*'|\([^()\n]*\)))?[ \t]*\)'''
)


def _links(text: str):
    prose = visible(text)
    for match in _WIKI.finditer(prose):
        yield match.group(0), match[1].split("|", 1)[0], True
    # 不把 wikilink 的显示文字再次解释为 Markdown 链接。
    prose = _WIKI.sub("", prose)
    for match in _MARKDOWN.finditer(prose):
        yield match.group(0), match[1].strip("<>"), False


@dataclass(frozen=True)
class _Reference:
    raw: str
    path: Path | None
    question: str | None = None
    error: str | None = None


class ReferenceIndex:
    """输入文档快照；隐藏链接写法、标题兼容与正文／附录的身份差异。"""

    def __init__(self, root: Path, documents: dict[Path, str], questions: dict[str, Path], compatibility: list[dict]):
        self.root = root.resolve()
        self.documents = {path.resolve(): text for path, text in documents.items()}
        self.owners = {path.resolve(): ident for ident, path in questions.items()}
        self.owners.update({
            path: path.stem for path in self.documents
            if path.parent == self.root / "附录" and path.stem in questions
        })
        self.legacy = {
            ((self.root / f'{item["domain"]}.md').resolve(), item["title"]): item["id"]
            for item in compatibility
        }
        self.questions = questions
        self._parsed: dict[Path, list[_Reference]] = {}
        self._headings: dict[Path, dict[str, str]] = {}

    def _text(self, path: Path) -> str:
        if path not in self.documents:
            self.documents[path] = path.read_text(encoding="utf-8-sig")
        return self.documents[path]

    def _heading(self, path: Path, anchor: str) -> str | None:
        if path not in self._headings:
            aliases = {}
            duplicates = {}
            for title in re.findall(r"^#{1,6} (.+)$", visible(self._text(path), inline=False), re.M):
                plain = re.sub(r"[`*_~]", "", title).strip()
                slug = re.sub(r"[^\w\-\s]", "", plain.casefold()).replace(" ", "-")
                number = duplicates.get(slug, 0)
                duplicates[slug] = number + 1
                for alias in [title, plain, slug + (f"-{number}" if number else "")]:
                    aliases.setdefault(alias, title)
            self._headings[path] = aliases
        return self._headings[path].get(anchor)

    def _resolve(self, source: Path, raw: str, target: str, wiki: bool) -> _Reference | None:
        # URL 不属于本地问题关系，也不在离线体检范围内。
        if re.match(r"[a-zA-Z][\w+.-]*:", target) and not re.match(r"^[a-zA-Z]:[\\/]", target):
            return None
        file, _, anchor = target.partition("#")
        file, anchor = unquote(unescape(file)), unquote(unescape(anchor))
        file = re.sub(r"\\([\\()[\] ])", r"\1", file)
        if file:
            base = self.root if wiki and not file.startswith(("./", "../")) else source.parent
            path = (base / file).resolve()
            if wiki and path.suffix != ".md" and path not in self.documents and not path.is_file():
                path = path.with_name(path.name + ".md")
        else:
            path = source
        if not path.is_relative_to(self.root) or (path not in self.documents and not path.is_file()):
            return _Reference(raw, path, error="无效链接")
        title = None
        if anchor:
            if path.suffix.lower() != ".md":
                return _Reference(raw, path, error="无效标题")
            title = self._heading(path, anchor)
            if title is None:
                return _Reference(raw, path, error="无效标题")
        question = self.owners.get(path) or self.legacy.get((path, title))
        if question and question not in self.questions:
            return _Reference(raw, path, error="兼容链接目标丢失")
        return _Reference(raw, path, question)

    def _references(self, source: Path) -> list[_Reference]:
        source = source.resolve()
        if source not in self._parsed:
            self._parsed[source] = [
                value for raw, target, wiki in _links(self._text(source))
                if (value := self._resolve(source, raw, target, wiki)) is not None
            ]
        return self._parsed[source]

    def errors(self) -> list[str]:
        return [
            f"{path.relative_to(self.root)}: {ref.error} {ref.raw}"
            for path in list(self.documents) for ref in self._references(path) if ref.error
        ]

    def links_to(self, source: Path, target: Path) -> bool:
        target = target.resolve()
        return any(ref.path == target and not ref.error for ref in self._references(source))

    def incoming(self, question: str) -> set[str]:
        return {
            owner for source, owner in self.owners.items() if owner != question
            for ref in self._references(source) if not ref.error and ref.question == question
        }

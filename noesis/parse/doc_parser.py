"""Markdown and plain text document parsing for Noesis."""

from pathlib import Path

from markdown_it import MarkdownIt
from pydantic import BaseModel, Field


class DocumentSection(BaseModel):
    title: str
    level: int
    start_line: int
    end_line: int


class DocumentLink(BaseModel):
    text: str
    url: str
    title: str | None = None
    start_line: int
    end_line: int


class DocumentCodeBlock(BaseModel):
    language: str | None = None
    content: str
    start_line: int
    end_line: int


class DocumentParagraph(BaseModel):
    text: str
    start_line: int
    end_line: int


class DocumentParseResult(BaseModel):
    file_path: Path
    title: str | None = None
    sections: list[DocumentSection] = Field(default_factory=list)
    links: list[DocumentLink] = Field(default_factory=list)
    code_blocks: list[DocumentCodeBlock] = Field(default_factory=list)
    paragraphs: list[DocumentParagraph] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def parse_document_file(
    file_path: Path, language: str | None = None
) -> DocumentParseResult:
    """Parse a Markdown or plain text document from disk."""
    resolved_language = language or _language_from_suffix(file_path)
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        return DocumentParseResult(
            file_path=file_path,
            errors=[f"failed to decode UTF-8 content: {error}"],
        )
    except OSError as error:
        return DocumentParseResult(
            file_path=file_path,
            errors=[f"failed to read document: {error}"],
        )

    if resolved_language == "markdown":
        return parse_markdown(file_path, content)
    if resolved_language in {"text", "txt", "log"}:
        return parse_text(file_path, content)

    return DocumentParseResult(
        file_path=file_path,
        errors=[f"unsupported document language: {resolved_language}"],
    )


def parse_markdown(file_path: Path, content: str) -> DocumentParseResult:
    """Parse Markdown content into document structure."""
    parser = MarkdownIt("commonmark")
    tokens = parser.parse(content)

    sections: list[DocumentSection] = []
    links: list[DocumentLink] = []
    code_blocks: list[DocumentCodeBlock] = []
    paragraphs: list[DocumentParagraph] = []

    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            inline = _next_inline(tokens, index)
            title = inline.content.strip() if inline is not None else ""
            start_line, end_line = _line_span(token)
            sections.append(
                DocumentSection(
                    title=title,
                    level=_heading_level(token.tag),
                    start_line=start_line,
                    end_line=end_line,
                )
            )
        elif token.type == "paragraph_open":
            inline = _next_inline(tokens, index)
            if inline is None:
                continue
            text = inline.content.strip()
            if not text:
                continue
            start_line, end_line = _line_span(token)
            paragraphs.append(
                DocumentParagraph(
                    text=text,
                    start_line=start_line,
                    end_line=end_line,
                )
            )
            links.extend(_links_from_inline(inline, start_line, end_line))
        elif token.type in {"fence", "code_block"}:
            start_line, end_line = _line_span(token)
            language = token.info.strip().split(maxsplit=1)[0] or None
            code_blocks.append(
                DocumentCodeBlock(
                    language=language,
                    content=token.content,
                    start_line=start_line,
                    end_line=end_line,
                )
            )

    return DocumentParseResult(
        file_path=file_path,
        title=_document_title(sections),
        sections=sections,
        links=links,
        code_blocks=code_blocks,
        paragraphs=paragraphs,
    )


def parse_text(file_path: Path, content: str) -> DocumentParseResult:
    """Parse plain text content into blank-line separated paragraphs."""
    paragraphs: list[DocumentParagraph] = []
    current_lines: list[str] = []
    start_line: int | None = None

    for line_number, line in enumerate(content.splitlines(), start=1):
        if line.strip():
            if start_line is None:
                start_line = line_number
            current_lines.append(line.rstrip())
            continue

        if current_lines and start_line is not None:
            paragraphs.append(
                DocumentParagraph(
                    text="\n".join(current_lines).strip(),
                    start_line=start_line,
                    end_line=line_number - 1,
                )
            )
            current_lines = []
            start_line = None

    if current_lines and start_line is not None:
        paragraphs.append(
            DocumentParagraph(
                text="\n".join(current_lines).strip(),
                start_line=start_line,
                end_line=start_line + len(current_lines) - 1,
            )
        )

    return DocumentParseResult(file_path=file_path, paragraphs=paragraphs)


def _language_from_suffix(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".md":
        return "markdown"
    if suffix in {".txt", ".log"}:
        return "text"
    return suffix.removeprefix(".") or "unknown"


def _document_title(sections: list[DocumentSection]) -> str | None:
    for section in sections:
        if section.level == 1:
            return section.title
    if sections:
        return sections[0].title
    return None


def _next_inline(tokens: list, index: int):
    if index + 1 >= len(tokens):
        return None
    inline = tokens[index + 1]
    if inline.type != "inline":
        return None
    return inline


def _links_from_inline(inline, start_line: int, end_line: int) -> list[DocumentLink]:
    links: list[DocumentLink] = []
    children = inline.children or []
    index = 0
    while index < len(children):
        child = children[index]
        if child.type != "link_open":
            index += 1
            continue

        url = _token_attr(child, "href")
        title = _token_attr(child, "title")
        link_text_parts: list[str] = []
        index += 1
        while index < len(children) and children[index].type != "link_close":
            if children[index].type in {"text", "code", "html_inline"}:
                link_text_parts.append(children[index].content)
            index += 1
        if url:
            links.append(
                DocumentLink(
                    text="".join(link_text_parts).strip(),
                    url=url,
                    title=title,
                    start_line=start_line,
                    end_line=end_line,
                )
            )
        index += 1
    return links


def _token_attr(token, name: str) -> str | None:
    value = token.attrGet(name)
    return value if value else None


def _line_span(token) -> tuple[int, int]:
    if token.map is None:
        return 0, 0
    return token.map[0] + 1, token.map[1]


def _heading_level(tag: str) -> int:
    if tag.startswith("h") and tag[1:].isdigit():
        return int(tag[1:])
    return 0

from pathlib import Path

from noesis.parse.doc_parser import (
    _code_block_language,
    parse_document_file,
    parse_markdown,
)

FIXTURES = Path(__file__).parent / "fixtures" / "parse"


def test_markdown_parser_extracts_sections_links_code_blocks_and_paragraphs() -> None:
    result = parse_document_file(FIXTURES / "guide.md", "markdown")

    assert result.errors == []
    assert result.title == "Noesis Guide"
    assert [(section.level, section.title) for section in result.sections] == [
        (1, "Noesis Guide"),
        (2, "Ingestion"),
        (3, "Documents"),
    ]
    assert [(link.text, link.url) for link in result.links] == [
        ("Architecture", "https://example.com/architecture"),
        ("local notes", "./notes.txt"),
    ]
    assert len(result.code_blocks) == 1
    assert result.code_blocks[0].language == "python"
    assert "def build_graph" in result.code_blocks[0].content
    assert [paragraph.text for paragraph in result.paragraphs] == [
        "Noesis turns local knowledge into a graph.",
        "[Architecture](https://example.com/architecture) and [local notes](./notes.txt)\n"
        "describe the parsing layer.",
        "Scan files and cache hashes.",
        "Parse Markdown and plain text documents.",
    ]


def test_document_parser_accepts_case_insensitive_language() -> None:
    result = parse_document_file(FIXTURES / "guide.md", "Markdown")

    assert result.errors == []
    assert result.title == "Noesis Guide"


def test_document_parser_recognizes_common_markdown_suffixes(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.markdown"
    file_path.write_text("# Markdown Extension\n", encoding="utf-8")

    result = parse_document_file(file_path)

    assert result.errors == []
    assert result.title == "Markdown Extension"


def test_text_parser_splits_paragraphs_on_blank_lines() -> None:
    result = parse_document_file(FIXTURES / "notes.txt", "text")

    assert result.errors == []
    assert [paragraph.text for paragraph in result.paragraphs] == [
        "First paragraph line one\ncontinues here.",
        "Second paragraph.",
        "Third paragraph\nwith multiple lines.",
    ]
    assert [
        (paragraph.start_line, paragraph.end_line) for paragraph in result.paragraphs
    ] == [
        (1, 2),
        (4, 4),
        (6, 7),
    ]


def test_markdown_parser_handles_untagged_code_blocks() -> None:
    result = parse_markdown(Path("untagged.md"), "```\nplain code\n```\n")

    assert result.errors == []
    assert len(result.code_blocks) == 1
    assert result.code_blocks[0].language is None
    assert result.code_blocks[0].content == "plain code\n"


def test_markdown_parser_extracts_rich_link_text() -> None:
    result = parse_markdown(Path("links.md"), "[`Module`\nAPI](./api.md)\n")

    assert result.errors == []
    assert [(link.text, link.url) for link in result.links] == [
        ("Module API", "./api.md")
    ]


def test_markdown_parser_extracts_heading_links() -> None:
    result = parse_markdown(Path("heading.md"), "# [API Reference](./api.md)\n")

    assert result.errors == []
    assert [(section.level, section.title) for section in result.sections] == [
        (1, "API Reference")
    ]
    assert [(link.text, link.url) for link in result.links] == [
        ("API Reference", "./api.md")
    ]


def test_markdown_parser_uses_image_alt_text_for_link_text() -> None:
    result = parse_markdown(
        Path("badge.md"),
        "[![Build Status](badge.svg)](https://ci.example.com)\n",
    )

    assert result.errors == []
    assert [(link.text, link.url) for link in result.links] == [
        ("Build Status", "https://ci.example.com")
    ]


def test_code_block_language_tolerates_none() -> None:
    assert _code_block_language(None) is None


def test_non_utf8_document_returns_errors(tmp_path: Path) -> None:
    file_path = tmp_path / "bad.txt"
    file_path.write_bytes(b"\xff\xfe\x00")

    result = parse_document_file(file_path, "text")

    assert result.paragraphs == []
    assert result.errors
    assert "failed to decode UTF-8 content" in result.errors[0]


def test_document_parse_result_is_json_serializable() -> None:
    result = parse_document_file(FIXTURES / "guide.md", "markdown")

    payload = result.model_dump_json()

    assert "Noesis Guide" in payload
    assert "https://example.com/architecture" in payload

from noesis.ingest.local_scanner import LocalScanner


def test_local_scanner_recognizes_common_markdown_suffixes(tmp_path) -> None:
    file_path = tmp_path / "README.markdown"
    file_path.write_text("# README\n", encoding="utf-8")

    files = LocalScanner().scan(tmp_path)

    scanned = {file.relative_path: file for file in files}
    assert scanned["README.markdown"].modality == "document"
    assert scanned["README.markdown"].language == "markdown"

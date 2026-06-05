"""Local directory scanner for Noesis."""

import fnmatch
from pathlib import Path

from pydantic import BaseModel

from noesis.core.config import Settings


class ScannedFile(BaseModel):
    path: Path
    relative_path: str
    suffix: str
    size_bytes: int
    modality: str
    language: str
    changed: bool = True


_MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn"}

_SUFFIX_TO_MODALITY: dict[str, str] = {
    ".py": "code",
    ".ts": "code",
    ".tsx": "code",
    ".js": "code",
    ".jsx": "code",
    ".go": "code",
    ".rs": "code",
    ".java": "code",
    ".c": "code",
    ".cpp": "code",
    ".h": "code",
    ".hpp": "code",
    ".txt": "document",
    ".log": "document",
    ".pdf": "document",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
}

_SUFFIX_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".txt": "text",
    ".log": "text",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
}

for suffix in _MARKDOWN_SUFFIXES:
    _SUFFIX_TO_MODALITY[suffix] = "document"
    _SUFFIX_TO_LANGUAGE[suffix] = "markdown"


class LocalScanner:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    def scan(self, directory: str | Path) -> list[ScannedFile]:
        root = Path(directory).resolve()
        if not root.is_dir():
            raise ValueError(f"not a directory: {root}")

        exclude_patterns = self._settings.ingest.exclude_patterns
        max_size = self._settings.ingest.max_file_size_mb * 1_024_000

        results: list[ScannedFile] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(root))
            if _is_excluded(relative, exclude_patterns):
                continue
            size = path.stat().st_size
            if size > max_size:
                continue
            suffix = path.suffix.lower()
            modality = _SUFFIX_TO_MODALITY.get(suffix, "unknown")
            language = _SUFFIX_TO_LANGUAGE.get(suffix, "unknown")
            results.append(
                ScannedFile(
                    path=path,
                    relative_path=relative,
                    suffix=suffix,
                    size_bytes=size,
                    modality=modality,
                    language=language,
                )
            )
        return results


def _is_excluded(relative_path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(
            relative_path.split("/")[0], pattern.removesuffix("/**")
        ):
            return True
    return False

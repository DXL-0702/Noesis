"""Code parser framework for Noesis."""

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field


class CodeSymbol(BaseModel):
    """Represents a code symbol extracted from source code."""

    id: str
    name: str
    kind: str
    file_path: Path
    start_line: int
    end_line: int
    text: str
    parent: str | None = None
    docstring: str | None = None


class CodeParseResult(BaseModel):
    """Result of parsing a code file."""

    file_path: Path
    language: str
    symbols: list[CodeSymbol] = Field(default_factory=list)
    imports: list[CodeSymbol] = Field(default_factory=list)
    exports: list[CodeSymbol] = Field(default_factory=list)
    calls: list[CodeSymbol] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    parse_error: str | None = None


class LanguageParser(ABC):
    """Abstract base class for language-specific parsers."""

    @abstractmethod
    def parse(self, file_path: Path, content: str) -> CodeParseResult:
        """Parse a code file and extract symbols.

        Args:
            file_path: Path to the file being parsed
            content: File content as string

        Returns:
            CodeParseResult with extracted symbols
        """
        pass

    @abstractmethod
    def language(self) -> str:
        """Return the language this parser handles."""
        pass


class CodeParserRegistry:
    """Registry for language-specific parsers."""

    def __init__(self) -> None:
        self._parsers: dict[str, LanguageParser] = {}

    def register(self, parser: LanguageParser) -> None:
        """Register a language parser."""
        self._parsers[parser.language()] = parser

    def get_parser(self, language: str) -> LanguageParser | None:
        """Get parser for a specific language."""
        return self._parsers.get(language)

    def parse_file(self, file_path: Path, language: str) -> CodeParseResult:
        """Parse a file using the appropriate language parser.

        Args:
            file_path: Path to the file
            language: Programming language

        Returns:
            CodeParseResult with extracted symbols or collected errors
        """
        parser = self.get_parser(language)
        if parser is None:
            error = f"unsupported language: {language}"
            return CodeParseResult(
                file_path=file_path,
                language=language,
                errors=[error],
                parse_error=error,
            )

        try:
            content = file_path.read_text(encoding="utf-8")
            return parser.parse(file_path, content)
        except Exception as e:
            return CodeParseResult(
                file_path=file_path,
                language=language,
                errors=[str(e)],
                parse_error=str(e),
            )


def stable_symbol_id(
    file_path: Path,
    kind: str,
    name: str,
    start_line: int,
    project_root: Path | None = None,
) -> str:
    """Build a stable symbol ID from path, symbol kind, name, and line."""
    path = file_path
    if project_root is not None:
        try:
            path = file_path.resolve().relative_to(project_root.resolve())
        except ValueError:
            path = file_path
    return f"{path.as_posix()}:{kind}:{name}:{start_line}"


# Global registry instance
_registry = CodeParserRegistry()


def register_parser(parser: LanguageParser) -> None:
    """Register a language parser to the global registry."""
    _registry.register(parser)


_builtins_registered = False


def _ensure_builtin_parsers() -> None:
    global _builtins_registered
    if _builtins_registered:
        return
    _builtins_registered = True
    import noesis.parse.python_parser  # noqa: F401
    import noesis.parse.typescript_parser  # noqa: F401


def parse_file(file_path: Path, language: str) -> CodeParseResult:
    """Parse a code file using the global registry.

    Args:
        file_path: Path to the file
        language: Programming language

    Returns:
        CodeParseResult with extracted symbols or collected errors
    """
    _ensure_builtin_parsers()
    return _registry.parse_file(file_path, language)

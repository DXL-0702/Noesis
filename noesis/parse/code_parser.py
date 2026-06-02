"""Code parser framework for Noesis."""

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class CodeSymbol(BaseModel):
    """Represents a code symbol (function, class, variable, etc.)."""

    name: str
    kind: str  # function, class, variable, import, etc.
    start_line: int
    end_line: int
    parent: str | None = None
    docstring: str | None = None


class CodeParseResult(BaseModel):
    """Result of parsing a code file."""

    file_path: Path
    language: str
    symbols: list[CodeSymbol]
    imports: list[str]
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

    def parse_file(self, file_path: Path, language: str) -> CodeParseResult | None:
        """Parse a file using the appropriate language parser.

        Args:
            file_path: Path to the file
            language: Programming language

        Returns:
            CodeParseResult if parser exists, None otherwise
        """
        parser = self.get_parser(language)
        if parser is None:
            return None

        try:
            content = file_path.read_text(encoding="utf-8")
            return parser.parse(file_path, content)
        except Exception as e:
            return CodeParseResult(
                file_path=file_path,
                language=language,
                symbols=[],
                imports=[],
                parse_error=str(e),
            )


# Global registry instance
_registry = CodeParserRegistry()


def register_parser(parser: LanguageParser) -> None:
    """Register a language parser to the global registry."""
    _registry.register(parser)


def parse_file(file_path: Path, language: str) -> CodeParseResult | None:
    """Parse a code file using the global registry.

    Args:
        file_path: Path to the file
        language: Programming language

    Returns:
        CodeParseResult if parser exists, None otherwise
    """
    return _registry.parse_file(file_path, language)

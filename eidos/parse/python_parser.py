"""Python code parser using tree-sitter."""

from pathlib import Path

from tree_sitter import Language, Parser
from tree_sitter_python import language

from eidos.parse.code_parser import (
    CodeParseResult,
    CodeSymbol,
    LanguageParser,
    register_parser,
)


class PythonParser(LanguageParser):
    """Python code parser using tree-sitter."""

    def __init__(self) -> None:
        self._parser = Parser(Language(language()))

    def language(self) -> str:
        return "python"

    def parse(self, file_path: Path, content: str) -> CodeParseResult:
        tree = self._parser.parse(bytes(content, "utf8"))
        root = tree.root_node

        symbols: list[CodeSymbol] = []
        imports: list[str] = []

        self._extract_symbols(root, content, symbols, imports)

        return CodeParseResult(
            file_path=file_path,
            language="python",
            symbols=symbols,
            imports=imports,
        )

    def _extract_symbols(
        self, node, content: str, symbols: list[CodeSymbol], imports: list[str]
    ) -> None:
        if node.type == "function_definition":
            self._extract_function(node, content, symbols)
        elif node.type == "class_definition":
            self._extract_class(node, content, symbols)
        elif node.type == "import_statement" or node.type == "import_from_statement":
            self._extract_import(node, content, imports)

        for child in node.children:
            self._extract_symbols(child, content, symbols, imports)

    def _extract_function(
        self, node, content: str, symbols: list[CodeSymbol], parent: str | None = None
    ) -> None:
        name_node = node.child_by_field_name("name")
        if name_node is None:
            return

        name = content[name_node.start_byte : name_node.end_byte]
        docstring = self._extract_docstring(node, content)

        symbols.append(
            CodeSymbol(
                name=name,
                kind="function",
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                parent=parent,
                docstring=docstring,
            )
        )

    def _extract_class(self, node, content: str, symbols: list[CodeSymbol]) -> None:
        name_node = node.child_by_field_name("name")
        if name_node is None:
            return

        name = content[name_node.start_byte : name_node.end_byte]
        docstring = self._extract_docstring(node, content)

        symbols.append(
            CodeSymbol(
                name=name,
                kind="class",
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                docstring=docstring,
            )
        )

        # Extract methods
        body = node.child_by_field_name("body")
        if body:
            for child in body.children:
                if child.type == "function_definition":
                    self._extract_function(child, content, symbols, parent=name)

    def _extract_import(self, node, content: str, imports: list[str]) -> None:
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    module = content[child.start_byte : child.end_byte]
                    imports.append(module)
        elif node.type == "import_from_statement":
            module_node = node.child_by_field_name("module_name")
            if module_node:
                module = content[module_node.start_byte : module_node.end_byte]
                imports.append(module)

    def _extract_docstring(self, node, content: str) -> str | None:
        body = node.child_by_field_name("body")
        if body and len(body.children) > 0:
            first_stmt = body.children[0]
            if first_stmt.type == "expression_statement":
                expr = first_stmt.children[0]
                if expr.type == "string":
                    docstring = content[expr.start_byte : expr.end_byte]
                    return docstring.strip('"""').strip("'''").strip()
        return None


# Auto-register on import
register_parser(PythonParser())

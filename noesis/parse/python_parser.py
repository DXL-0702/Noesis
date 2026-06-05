"""Python code parser using tree-sitter."""

from pathlib import Path

from tree_sitter import Language, Parser
from tree_sitter_python import language

from noesis.parse.code_parser import (
    CodeParseResult,
    CodeSymbol,
    LanguageParser,
    register_parser,
    stable_symbol_id,
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
        imports: list[CodeSymbol] = []
        calls: list[CodeSymbol] = []
        errors: list[str] = []

        if root.has_error:
            errors.append("syntax error detected by tree-sitter")

        self._extract_symbols(root, file_path, content, symbols, imports, calls)

        return CodeParseResult(
            file_path=file_path,
            language="python",
            symbols=symbols,
            imports=imports,
            calls=calls,
            errors=errors,
            parse_error=errors[0] if errors else None,
        )

    def _extract_symbols(
        self,
        node,
        file_path: Path,
        content: str,
        symbols: list[CodeSymbol],
        imports: list[CodeSymbol],
        calls: list[CodeSymbol],
        parent: str | None = None,
        parent_kind: str | None = None,
    ) -> None:
        if node.type == "function_definition":
            self._extract_function(
                node, file_path, content, symbols, parent, parent_kind
            )
            parent = self._node_name(node, content) or parent
            parent_kind = "function"
        elif node.type == "class_definition":
            self._extract_class(node, file_path, content, symbols)
            parent = self._node_name(node, content) or parent
            parent_kind = "class"
        elif node.type == "import_statement" or node.type == "import_from_statement":
            self._extract_import(node, file_path, content, imports)
        elif node.type == "call":
            self._extract_call(node, file_path, content, calls, parent)

        for child in node.children:
            self._extract_symbols(
                child,
                file_path,
                content,
                symbols,
                imports,
                calls,
                parent,
                parent_kind,
            )

    def _extract_function(
        self,
        node,
        file_path: Path,
        content: str,
        symbols: list[CodeSymbol],
        parent: str | None = None,
        parent_kind: str | None = None,
    ) -> None:
        name = self._node_name(node, content)
        if name is None:
            return

        docstring = self._extract_docstring(node, content)
        kind = "method" if parent_kind == "class" else "function"
        start_line = node.start_point[0] + 1

        symbols.append(
            CodeSymbol(
                id=stable_symbol_id(file_path, kind, name, start_line),
                name=name,
                kind=kind,
                file_path=file_path,
                start_line=start_line,
                end_line=node.end_point[0] + 1,
                text=self._node_text(node, content),
                parent=parent,
                docstring=docstring,
            )
        )

    def _extract_class(
        self, node, file_path: Path, content: str, symbols: list[CodeSymbol]
    ) -> None:
        name = self._node_name(node, content)
        if name is None:
            return

        docstring = self._extract_docstring(node, content)
        start_line = node.start_point[0] + 1

        symbols.append(
            CodeSymbol(
                id=stable_symbol_id(file_path, "class", name, start_line),
                name=name,
                kind="class",
                file_path=file_path,
                start_line=start_line,
                end_line=node.end_point[0] + 1,
                text=self._node_text(node, content),
                docstring=docstring,
            )
        )

    def _extract_import(
        self, node, file_path: Path, content: str, imports: list[CodeSymbol]
    ) -> None:
        names: list[str] = []
        if node.type == "import_statement":
            names = [
                self._node_text(child, content)
                for child in node.children
                if child.type == "dotted_name"
            ]
        elif node.type == "import_from_statement":
            module_node = node.child_by_field_name("module_name")
            if module_node:
                names = [self._node_text(module_node, content)]

        for name in names:
            start_line = node.start_point[0] + 1
            imports.append(
                CodeSymbol(
                    id=stable_symbol_id(file_path, "import", name, start_line),
                    name=name,
                    kind="import",
                    file_path=file_path,
                    start_line=start_line,
                    end_line=node.end_point[0] + 1,
                    text=self._node_text(node, content),
                )
            )

    def _extract_call(
        self,
        node,
        file_path: Path,
        content: str,
        calls: list[CodeSymbol],
        parent: str | None,
    ) -> None:
        function_node = node.child_by_field_name("function")
        if function_node is None:
            return
        name = self._node_text(function_node, content)
        start_line = node.start_point[0] + 1
        calls.append(
            CodeSymbol(
                id=stable_symbol_id(file_path, "call", name, start_line),
                name=name,
                kind="call",
                file_path=file_path,
                start_line=start_line,
                end_line=node.end_point[0] + 1,
                text=self._node_text(node, content),
                parent=parent,
            )
        )

    def _extract_docstring(self, node, content: str) -> str | None:
        body = node.child_by_field_name("body")
        if body and len(body.children) > 0:
            first_stmt = body.children[0]
            if first_stmt.type == "expression_statement":
                expr = first_stmt.children[0]
                if expr.type == "string":
                    docstring = content[expr.start_byte : expr.end_byte]
                    # Remove triple quotes using removeprefix/removesuffix
                    docstring = docstring.strip()
                    if docstring.startswith('"""') and docstring.endswith('"""'):
                        return docstring[3:-3].strip()
                    if docstring.startswith("'''") and docstring.endswith("'''"):
                        return docstring[3:-3].strip()
                    return docstring
        return None

    def _node_name(self, node, content: str) -> str | None:
        name_node = node.child_by_field_name("name")
        if name_node is None:
            return None
        return self._node_text(name_node, content)

    def _node_text(self, node, content: str) -> str:
        return content[node.start_byte : node.end_byte]


# Auto-register on import
register_parser(PythonParser())

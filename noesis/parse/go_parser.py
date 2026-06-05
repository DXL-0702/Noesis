"""Go code parser using tree-sitter."""

from pathlib import Path

from tree_sitter import Language, Parser
from tree_sitter_go import language

from noesis.parse.code_parser import (
    CodeParseResult,
    CodeSymbol,
    LanguageParser,
    register_parser,
    stable_symbol_id,
)


class GoParser(LanguageParser):
    """Go code parser using tree-sitter."""

    def __init__(self) -> None:
        self._parser = Parser(Language(language()))

    def language(self) -> str:
        return "go"

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
            language="go",
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
    ) -> None:
        next_parent = parent

        if node.type == "package_clause":
            self._extract_package(node, file_path, content, symbols)
        elif node.type == "import_declaration":
            self._extract_imports(node, file_path, content, imports)
        elif node.type == "function_declaration":
            self._extract_function(node, file_path, content, symbols)
            next_parent = self._node_name(node, content) or parent
        elif node.type == "method_declaration":
            receiver_name = self._receiver_name(node, content)
            self._extract_method(node, file_path, content, symbols, receiver_name)
            next_parent = self._node_name(node, content) or parent
        elif node.type == "call_expression":
            self._extract_call(node, file_path, content, calls, parent)

        for child in node.children:
            self._extract_symbols(
                child,
                file_path,
                content,
                symbols,
                imports,
                calls,
                next_parent,
            )

    def _extract_package(
        self, node, file_path: Path, content: str, symbols: list[CodeSymbol]
    ) -> None:
        name_node = self._first_child_of_type(node, "package_identifier")
        if name_node is None:
            return
        name = self._node_text(name_node, content)
        start_line = node.start_point[0] + 1
        symbols.append(
            CodeSymbol(
                id=stable_symbol_id(file_path, "package", name, start_line),
                name=name,
                kind="package",
                file_path=file_path,
                start_line=start_line,
                end_line=node.end_point[0] + 1,
                text=self._node_text(node, content),
            )
        )

    def _extract_imports(
        self, node, file_path: Path, content: str, imports: list[CodeSymbol]
    ) -> None:
        for import_spec in self._walk(node):
            if import_spec.type != "import_spec":
                continue
            path_node = import_spec.child_by_field_name("path")
            if path_node is None:
                continue
            name = self._clean_import_path(self._node_text(path_node, content))
            start_line = import_spec.start_point[0] + 1
            imports.append(
                CodeSymbol(
                    id=stable_symbol_id(file_path, "import", name, start_line),
                    name=name,
                    kind="import",
                    file_path=file_path,
                    start_line=start_line,
                    end_line=import_spec.end_point[0] + 1,
                    text=self._node_text(import_spec, content),
                )
            )

    def _extract_function(
        self, node, file_path: Path, content: str, symbols: list[CodeSymbol]
    ) -> None:
        name = self._node_name(node, content)
        if name is None:
            return
        start_line = node.start_point[0] + 1
        symbols.append(
            CodeSymbol(
                id=stable_symbol_id(file_path, "function", name, start_line),
                name=name,
                kind="function",
                file_path=file_path,
                start_line=start_line,
                end_line=node.end_point[0] + 1,
                text=self._node_text(node, content),
            )
        )

    def _extract_method(
        self,
        node,
        file_path: Path,
        content: str,
        symbols: list[CodeSymbol],
        receiver_name: str | None,
    ) -> None:
        name = self._node_name(node, content)
        if name is None:
            return
        start_line = node.start_point[0] + 1
        symbols.append(
            CodeSymbol(
                id=stable_symbol_id(file_path, "method", name, start_line),
                name=name,
                kind="method",
                file_path=file_path,
                start_line=start_line,
                end_line=node.end_point[0] + 1,
                text=self._node_text(node, content),
                parent=receiver_name,
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

    def _node_name(self, node, content: str) -> str | None:
        name_node = node.child_by_field_name("name")
        if name_node is None:
            return None
        return self._node_text(name_node, content)

    def _receiver_name(self, node, content: str) -> str | None:
        receiver_node = node.child_by_field_name("receiver")
        if receiver_node is None:
            return None
        for child in self._walk(receiver_node):
            if child.type in {"type_identifier", "qualified_type"}:
                return self._node_text(child, content)
        return None

    def _first_child_of_type(self, node, node_type: str):
        for child in node.children:
            if child.type == node_type:
                return child
        return None

    def _clean_import_path(self, value: str) -> str:
        return value.strip().strip('"')

    def _node_text(self, node, content: str) -> str:
        return content[node.start_byte : node.end_byte]

    def _walk(self, node):
        yield node
        for child in node.children:
            yield from self._walk(child)


register_parser(GoParser())

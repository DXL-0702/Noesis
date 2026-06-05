"""TypeScript and JavaScript code parser using tree-sitter."""

from pathlib import Path

from tree_sitter import Language, Parser
from tree_sitter_javascript import language as javascript_language
from tree_sitter_typescript import language_tsx, language_typescript

from noesis.parse.code_parser import (
    CodeParseResult,
    CodeSymbol,
    LanguageParser,
    register_parser,
    stable_symbol_id,
)


class TypeScriptParser(LanguageParser):
    """TypeScript and JavaScript parser using tree-sitter grammars."""

    def __init__(self, language_name: str) -> None:
        if language_name not in {"javascript", "typescript"}:
            raise ValueError(f"unsupported TS/JS language: {language_name}")
        self._language_name = language_name
        self._javascript_parser = Parser(Language(javascript_language()))
        self._typescript_parser = Parser(Language(language_typescript()))
        self._tsx_parser = Parser(Language(language_tsx()))

    def language(self) -> str:
        return self._language_name

    def parse(self, file_path: Path, content: str) -> CodeParseResult:
        parser = self._select_parser(file_path)
        tree = parser.parse(bytes(content, "utf8"))
        root = tree.root_node

        symbols: list[CodeSymbol] = []
        imports: list[CodeSymbol] = []
        exports: list[CodeSymbol] = []
        calls: list[CodeSymbol] = []
        errors: list[str] = []

        if root.has_error:
            errors.append("syntax error detected by tree-sitter")

        self._extract_symbols(
            root, file_path, content, symbols, imports, exports, calls
        )

        return CodeParseResult(
            file_path=file_path,
            language=self._language_name,
            symbols=symbols,
            imports=imports,
            exports=exports,
            calls=calls,
            errors=errors,
            parse_error=errors[0] if errors else None,
        )

    def _select_parser(self, file_path: Path) -> Parser:
        suffix = file_path.suffix.lower()
        if suffix == ".tsx":
            return self._tsx_parser
        if suffix == ".ts":
            return self._typescript_parser
        return self._javascript_parser

    def _extract_symbols(
        self,
        node,
        file_path: Path,
        content: str,
        symbols: list[CodeSymbol],
        imports: list[CodeSymbol],
        exports: list[CodeSymbol],
        calls: list[CodeSymbol],
        parent: str | None = None,
        parent_kind: str | None = None,
    ) -> None:
        next_parent = parent
        next_parent_kind = parent_kind

        if node.type == "function_declaration":
            self._extract_named_function(
                node, file_path, content, symbols, parent, parent_kind
            )
            next_parent = self._node_name(node, content) or parent
            next_parent_kind = "function"
        elif node.type in {"class_declaration", "abstract_class_declaration"}:
            self._extract_class(node, file_path, content, symbols)
            next_parent = self._node_name(node, content) or parent
            next_parent_kind = "class"
        elif node.type == "method_definition":
            self._extract_method(node, file_path, content, symbols, parent)
            next_parent = self._node_name(node, content) or parent
            next_parent_kind = "method"
        elif node.type in {"lexical_declaration", "variable_declaration"}:
            extracted_name = self._extract_arrow_functions(
                node, file_path, content, symbols, parent
            )
            if extracted_name is not None:
                next_parent = extracted_name
                next_parent_kind = "function"
        elif node.type == "import_statement":
            self._extract_import(node, file_path, content, imports)
        elif node.type == "export_statement":
            self._extract_export(node, file_path, content, exports)
        elif node.type == "call_expression":
            self._extract_call(node, file_path, content, calls, parent)

        for child in node.children:
            self._extract_symbols(
                child,
                file_path,
                content,
                symbols,
                imports,
                exports,
                calls,
                next_parent,
                next_parent_kind,
            )

    def _extract_named_function(
        self,
        node,
        file_path: Path,
        content: str,
        symbols: list[CodeSymbol],
        parent: str | None,
        parent_kind: str | None,
    ) -> None:
        name = self._node_name(node, content)
        if name is None:
            return
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
            )
        )

    def _extract_class(
        self, node, file_path: Path, content: str, symbols: list[CodeSymbol]
    ) -> None:
        name = self._node_name(node, content)
        if name is None:
            return
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
            )
        )

    def _extract_method(
        self,
        node,
        file_path: Path,
        content: str,
        symbols: list[CodeSymbol],
        parent: str | None,
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
                parent=parent,
            )
        )

    def _extract_arrow_functions(
        self,
        node,
        file_path: Path,
        content: str,
        symbols: list[CodeSymbol],
        parent: str | None,
    ) -> str | None:
        extracted_name: str | None = None
        for declarator in self._walk(node):
            if declarator.type != "variable_declarator":
                continue
            value_node = declarator.child_by_field_name("value")
            if value_node is None or value_node.type not in {
                "arrow_function",
                "function_expression",
            }:
                continue
            name_node = declarator.child_by_field_name("name")
            if name_node is None:
                continue
            name = self._node_text(name_node, content)
            start_line = declarator.start_point[0] + 1
            symbols.append(
                CodeSymbol(
                    id=stable_symbol_id(file_path, "function", name, start_line),
                    name=name,
                    kind="function",
                    file_path=file_path,
                    start_line=start_line,
                    end_line=declarator.end_point[0] + 1,
                    text=self._node_text(declarator, content),
                    parent=parent,
                )
            )
            extracted_name = name
        return extracted_name

    def _extract_import(
        self, node, file_path: Path, content: str, imports: list[CodeSymbol]
    ) -> None:
        source_node = node.child_by_field_name("source")
        name = (
            self._clean_string(self._node_text(source_node, content))
            if source_node is not None
            else self._node_text(node, content)
        )
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

    def _extract_export(
        self, node, file_path: Path, content: str, exports: list[CodeSymbol]
    ) -> None:
        name = self._export_name(node, content)
        start_line = node.start_point[0] + 1
        exports.append(
            CodeSymbol(
                id=stable_symbol_id(file_path, "export", name, start_line),
                name=name,
                kind="export",
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

    def _node_name(self, node, content: str) -> str | None:
        name_node = node.child_by_field_name("name")
        if name_node is None:
            for child in node.children:
                if child.type in {
                    "property_identifier",
                    "identifier",
                    "private_property_identifier",
                }:
                    name_node = child
                    break
        if name_node is None:
            return None
        return self._node_text(name_node, content)

    def _export_name(self, node, content: str) -> str:
        source_node = node.child_by_field_name("source")
        if source_node is not None:
            return self._clean_string(self._node_text(source_node, content))
        value_node = node.child_by_field_name("value")
        if value_node is not None:
            return self._node_text(value_node, content)
        declaration_node = node.child_by_field_name("declaration")
        if declaration_node is not None:
            declaration_name = self._node_name(declaration_node, content)
            if declaration_name is not None:
                return declaration_name
        for child in node.children:
            if child.type in {"export_clause", "namespace_export"}:
                return self._node_text(child, content)
        return self._node_text(node, content)

    def _clean_string(self, value: str) -> str:
        return value.strip().strip("\"'")

    def _node_text(self, node, content: str) -> str:
        return content[node.start_byte : node.end_byte]

    def _walk(self, node):
        yield node
        for child in node.children:
            yield from self._walk(child)


register_parser(TypeScriptParser("javascript"))
register_parser(TypeScriptParser("typescript"))

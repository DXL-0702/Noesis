from pathlib import Path

from noesis.parse.code_parser import parse_file

FIXTURES = Path(__file__).parent / "fixtures" / "parse"


def test_typescript_parser_extracts_tsx_symbols_imports_exports_and_calls() -> None:
    result = parse_file(FIXTURES / "app.tsx", "typescript")

    assert result.errors == []
    assert _names(result.imports) == {"react", "./view"}
    assert "UserCard" in _names(result.exports)
    assert {"formatName", "UserCard", "UserService", "load"} <= _names(result.symbols)
    assert _kinds_by_name(result.symbols)["UserCard"] == "function"
    assert _kinds_by_name(result.symbols)["UserService"] == "class"
    assert _kinds_by_name(result.symbols)["load"] == "method"
    assert {"formatName", "render", "fetch"} <= _names(result.calls)

    user_card = _symbol(result.symbols, "UserCard")
    assert user_card.id.endswith(":function:UserCard:12")
    assert user_card.text.startswith("UserCard =")


def test_javascript_parser_extracts_functions_and_function_expressions() -> None:
    result = parse_file(FIXTURES / "utils.js", "javascript")

    assert result.errors == []
    assert _names(result.imports) == {"path"}
    assert "joinPath" in _names(result.exports)
    assert {"joinPath", "logger"} <= _names(result.symbols)
    assert {"path.join", "console.log", "logger", "joinPath"} <= _names(result.calls)


def test_python_parser_keeps_phase_2_contract() -> None:
    result = parse_file(FIXTURES / "sample.py", "python")

    assert result.errors == []
    assert _names(result.imports) == {"os", "pathlib"}
    assert {"normalize", "Loader", "load"} <= _names(result.symbols)
    assert _kinds_by_name(result.symbols)["load"] == "method"
    assert {"value.strip", "normalize", "Path", "os.getcwd"} <= _names(result.calls)


def test_go_parser_extracts_package_imports_functions_methods_and_calls() -> None:
    result = parse_file(FIXTURES / "service.go", "go")

    assert result.errors == []
    assert _names(result.imports) == {"fmt", "net/http"}
    assert {"service", "NewUserService", "Load", "normalize"} <= _names(result.symbols)
    assert _kinds_by_name(result.symbols)["service"] == "package"
    assert _kinds_by_name(result.symbols)["NewUserService"] == "function"
    assert _kinds_by_name(result.symbols)["normalize"] == "function"
    assert _kinds_by_name(result.symbols)["Load"] == "method"
    assert _symbol(result.symbols, "Load").parent == "UserService"
    assert {"fmt.Println", "http.Get", "normalize"} <= _names(result.calls)

    load = _symbol(result.symbols, "Load")
    assert load.id.endswith(":method:Load:14")
    assert load.text.startswith("func (s *UserService) Load")


def test_unsupported_language_returns_clear_error() -> None:
    result = parse_file(FIXTURES / "sample.py", "ruby")

    assert result.symbols == []
    assert result.parse_error == "unsupported language: ruby"
    assert result.errors == ["unsupported language: ruby"]


def _names(symbols) -> set[str]:
    return {symbol.name for symbol in symbols}


def _kinds_by_name(symbols) -> dict[str, str]:
    return {symbol.name: symbol.kind for symbol in symbols}


def _symbol(symbols, name: str):
    for symbol in symbols:
        if symbol.name == name:
            return symbol
    raise AssertionError(f"missing symbol: {name}")

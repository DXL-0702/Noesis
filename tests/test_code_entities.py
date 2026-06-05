from pathlib import Path

from noesis.core.constants import ConfidenceLabel, RelationType
from noesis.core.types import Entity, Relation
from noesis.parse.code_entities import symbols_to_entities, symbols_to_relations
from noesis.parse.code_parser import parse_file

FIXTURES = Path(__file__).parent / "fixtures" / "parse"


def test_python_symbols_convert_to_entities_and_relations() -> None:
    result = parse_file(FIXTURES / "sample.py", "python")
    entities = symbols_to_entities(result)
    relations = symbols_to_relations(result)

    assert {"sample.py", "normalize", "Loader", "load", "os", "pathlib"} <= _names(
        entities
    )
    assert _types(relations) >= {
        RelationType.DEFINES.value,
        RelationType.IMPORTS.value,
        RelationType.CONTAINS.value,
        RelationType.CALLS.value,
    }
    assert _has_relation(entities, relations, "sample.py", "DEFINES", "Loader")
    assert _has_relation(entities, relations, "Loader", "CONTAINS", "load")
    assert _has_relation(entities, relations, "sample.py", "IMPORTS", "pathlib")
    assert _has_relation(entities, relations, "load", "CALLS", "normalize")

    assert {entity.confidence for entity in entities} == {
        ConfidenceLabel.EXTRACTED.value
    }
    assert {relation.extractor for relation in relations} == {"tree-sitter"}


def test_typescript_symbols_convert_to_entities_and_relations() -> None:
    result = parse_file(FIXTURES / "app.tsx", "typescript")
    entities = symbols_to_entities(result)
    relations = symbols_to_relations(result)

    assert {"app.tsx", "UserCard", "UserService", "load", "react"} <= _names(entities)
    assert _has_relation(entities, relations, "app.tsx", "DEFINES", "UserCard")
    assert _has_relation(entities, relations, "UserService", "CONTAINS", "load")
    assert _has_relation(entities, relations, "app.tsx", "IMPORTS", "react")
    assert _has_relation(entities, relations, "UserCard", "CALLS", "render")
    assert _has_relation(entities, relations, "load", "CALLS", "fetch")


def test_go_symbols_convert_package_and_calls() -> None:
    result = parse_file(FIXTURES / "service.go", "go")
    entities = symbols_to_entities(result)
    relations = symbols_to_relations(result)

    assert {"service.go", "service", "NewUserService", "Load", "fmt"} <= _names(
        entities
    )
    assert _has_relation(entities, relations, "service.go", "DEFINES", "service")
    assert _has_relation(entities, relations, "service.go", "IMPORTS", "net/http")
    assert _has_relation(entities, relations, "Load", "CALLS", "http.Get")


def test_entity_and_relation_ids_are_stable() -> None:
    first = parse_file(FIXTURES / "app.tsx", "typescript")
    second = parse_file(FIXTURES / "app.tsx", "typescript")

    assert _ids(symbols_to_entities(first)) == _ids(symbols_to_entities(second))
    assert _ids(symbols_to_relations(first)) == _ids(symbols_to_relations(second))


def _names(entities: list[Entity]) -> set[str]:
    return {entity.name for entity in entities}


def _types(relations: list[Relation]) -> set[str]:
    return {relation.type for relation in relations}


def _ids(items: list[Entity] | list[Relation]) -> list[str]:
    return [item.id for item in items]


def _has_relation(
    entities: list[Entity],
    relations: list[Relation],
    source_name: str,
    relation_type: str,
    target_name: str,
) -> bool:
    entities_by_id = {entity.id: entity for entity in entities}
    for relation in relations:
        source = entities_by_id[relation.source_entity_id]
        target = entities_by_id[relation.target_entity_id]
        if (
            source.name == source_name
            and relation.type == relation_type
            and target.name == target_name
        ):
            return True
    return False

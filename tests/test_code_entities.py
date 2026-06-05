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
    assert not _has_relation(entities, relations, "app.tsx", "DEFINES", "load")
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


def test_module_level_calls_are_attributed_to_file() -> None:
    result = parse_file(FIXTURES / "utils.js", "javascript")
    entities = symbols_to_entities(result)
    relations = symbols_to_relations(result)

    assert _has_relation(entities, relations, "utils.js", "CALLS", "logger")
    assert _has_relation(entities, relations, "utils.js", "CALLS", "joinPath")


def test_calls_resolve_to_correct_symbol_when_names_collide() -> None:
    result = parse_file(FIXTURES / "collision.py", "python")
    entities = symbols_to_entities(result)
    relations = symbols_to_relations(result)

    alpha_load_ids = _contained_entity_ids(entities, relations, "Alpha", "load")
    beta_load_ids = _contained_entity_ids(entities, relations, "Beta", "load")

    assert len(alpha_load_ids) == 1
    assert len(beta_load_ids) == 1

    alpha_calls = _called_names_from_entity_ids(entities, relations, alpha_load_ids)
    beta_calls = _called_names_from_entity_ids(entities, relations, beta_load_ids)

    assert "first" in alpha_calls
    assert "second" not in alpha_calls
    assert "second" in beta_calls
    assert "first" not in beta_calls


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


def _contained_entity_ids(
    entities: list[Entity],
    relations: list[Relation],
    parent_name: str,
    child_name: str,
) -> list[str]:
    entities_by_id = {entity.id: entity for entity in entities}
    return [
        relation.target_entity_id
        for relation in relations
        if relation.type == RelationType.CONTAINS.value
        and entities_by_id[relation.source_entity_id].name == parent_name
        and entities_by_id[relation.target_entity_id].name == child_name
    ]


def _called_names_from_entity_ids(
    entities: list[Entity],
    relations: list[Relation],
    source_entity_ids: list[str],
) -> set[str]:
    entities_by_id = {entity.id: entity for entity in entities}
    return {
        entities_by_id[relation.target_entity_id].name
        for relation in relations
        if relation.type == RelationType.CALLS.value
        and relation.source_entity_id in source_entity_ids
    }

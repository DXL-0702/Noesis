"""Convert parsed code symbols into Noesis entities and relations."""

from pathlib import Path

from noesis.core.constants import ConfidenceLabel, RelationType
from noesis.core.types import Entity, Relation
from noesis.parse.code_parser import CodeParseResult, CodeSymbol

_EXTRACTOR = "tree-sitter"
_MODALITY = "code"


def symbols_to_entities(result: CodeParseResult) -> list[Entity]:
    """Convert a code parse result into deterministic entities."""
    entities = [_file_entity(result.file_path)]
    for symbol in [
        *result.symbols,
        *result.imports,
        *result.exports,
        *result.calls,
    ]:
        entities.append(_symbol_entity(symbol, result.file_path))
    return _dedupe_entities(entities)


def symbols_to_relations(result: CodeParseResult) -> list[Relation]:
    """Convert a code parse result into deterministic relations."""
    file_entity_id = _file_entity_id(result.file_path)
    symbol_by_name = _symbols_by_name(result.symbols)

    relations: list[Relation] = []

    for symbol in result.symbols:
        relations.append(
            _relation(file_entity_id, RelationType.DEFINES.value, symbol.id)
        )
        if symbol.kind == "method" and symbol.parent:
            parent_symbol = _resolve_symbol_at_line(
                symbol_by_name.get(symbol.parent, []),
                symbol.start_line,
            )
            if parent_symbol is not None:
                relations.append(
                    _relation(
                        parent_symbol.id,
                        RelationType.CONTAINS.value,
                        symbol.id,
                    )
                )

    for import_symbol in result.imports:
        relations.append(
            _relation(file_entity_id, RelationType.IMPORTS.value, import_symbol.id)
        )

    for call in result.calls:
        if call.parent is None:
            continue
        caller = _resolve_symbol_at_line(
            symbol_by_name.get(call.parent, []),
            call.start_line,
        )
        if caller is None:
            continue
        relations.append(_relation(caller.id, RelationType.CALLS.value, call.id))

    return _dedupe_relations(relations)


def _file_entity(file_path: Path) -> Entity:
    path = file_path.as_posix()
    return Entity(
        id=_file_entity_id(file_path),
        name=file_path.name,
        type="file",
        modality=_MODALITY,
        source_id=path,
        document_id=path,
        confidence=ConfidenceLabel.EXTRACTED.value,
        extractor=_EXTRACTOR,
    )


def _symbol_entity(symbol: CodeSymbol, file_path: Path) -> Entity:
    path = file_path.as_posix()
    return Entity(
        id=symbol.id,
        name=symbol.name,
        type=symbol.kind,
        modality=_MODALITY,
        source_id=path,
        document_id=path,
        confidence=ConfidenceLabel.EXTRACTED.value,
        extractor=_EXTRACTOR,
    )


def _relation(source_id: str, relation_type: str, target_id: str) -> Relation:
    return Relation(
        id=f"relation:{source_id}:{relation_type}:{target_id}",
        source_entity_id=source_id,
        target_entity_id=target_id,
        type=relation_type,
        confidence=ConfidenceLabel.EXTRACTED.value,
        extractor=_EXTRACTOR,
    )


def _file_entity_id(file_path: Path) -> str:
    return f"file:{file_path.as_posix()}"


def _symbols_by_name(symbols: list[CodeSymbol]) -> dict[str, list[CodeSymbol]]:
    result: dict[str, list[CodeSymbol]] = {}
    for symbol in symbols:
        result.setdefault(symbol.name, []).append(symbol)
    return result


def _resolve_symbol_at_line(
    candidates: list[CodeSymbol], line: int
) -> CodeSymbol | None:
    matching = [
        candidate
        for candidate in candidates
        if candidate.start_line <= line <= candidate.end_line
    ]
    if not matching:
        return None
    return min(
        matching,
        key=lambda candidate: (
            candidate.end_line - candidate.start_line,
            candidate.start_line,
        ),
    )


def _dedupe_entities(entities: list[Entity]) -> list[Entity]:
    by_id: dict[str, Entity] = {}
    for entity in entities:
        by_id.setdefault(entity.id, entity)
    return list(by_id.values())


def _dedupe_relations(relations: list[Relation]) -> list[Relation]:
    by_id: dict[str, Relation] = {}
    for relation in relations:
        by_id.setdefault(relation.id, relation)
    return list(by_id.values())

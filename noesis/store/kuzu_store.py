"""Kuzu graph database implementation."""

import pathlib
from typing import Any

import kuzu

from noesis.core.types import Entity, Path, Relation
from noesis.store.base import GraphStore


class KuzuStore(GraphStore):
    def __init__(self) -> None:
        self._db: kuzu.Database | None = None
        self._conn: kuzu.Connection | None = None
        self._db_path: pathlib.Path | None = None

    def connect(self, db_path: str) -> "KuzuStore":
        path = pathlib.Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = path
        self._db = kuzu.Database(str(path))
        self._conn = kuzu.Connection(self._db)
        self._init_schema()
        return self

    def _connection(self) -> kuzu.Connection:
        if self._conn is None:
            raise RuntimeError("KuzuStore is not connected")
        return self._conn

    def _init_schema(self) -> None:
        entity_table = "CREATE NODE TABLE IF NOT EXISTS Entity(id STRING PRIMARY KEY, name STRING, type STRING, modality STRING, source_id STRING, document_id STRING, chunk_id STRING, confidence STRING, extractor STRING)"
        rel_table = "CREATE REL TABLE IF NOT EXISTS RELATION(FROM Entity TO Entity, id STRING, type STRING, confidence STRING, extractor STRING)"
        conn = self._connection()
        conn.execute(entity_table)
        conn.execute(rel_table)

    def upsert_node(self, entity: Entity) -> None:
        query = """
            MATCH (e:Entity {id: $id})
            RETURN e.id
        """
        result = self._connection().execute(query, parameters={"id": entity.id})
        exists = result.has_next()
        if exists:
            self._connection().execute(
                """
                MATCH (e:Entity {id: $id})
                SET e.name = $name, e.type = $type, e.modality = $modality,
                    e.source_id = $source_id, e.document_id = $document_id,
                    e.chunk_id = $chunk_id, e.confidence = $confidence,
                    e.extractor = $extractor
                """,
                parameters={
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "modality": entity.modality,
                    "source_id": entity.source_id,
                    "document_id": entity.document_id,
                    "chunk_id": entity.chunk_id,
                    "confidence": entity.confidence,
                    "extractor": entity.extractor,
                },
            )
        else:
            self._connection().execute(
                """
                CREATE (e:Entity {id: $id, name: $name, type: $type,
                    modality: $modality, source_id: $source_id,
                    document_id: $document_id, chunk_id: $chunk_id,
                    confidence: $confidence, extractor: $extractor})
                """,
                parameters={
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "modality": entity.modality,
                    "source_id": entity.source_id,
                    "document_id": entity.document_id,
                    "chunk_id": entity.chunk_id,
                    "confidence": entity.confidence,
                    "extractor": entity.extractor,
                },
            )

    def upsert_edge(self, relation: Relation) -> None:
        query = """
            MATCH (a:Entity {id: $src})-[r:RELATION]->(b:Entity {id: $tgt})
            WHERE r.type = $type
            RETURN r.type
        """
        result = self._connection().execute(
            query,
            parameters={
                "src": relation.source_entity_id,
                "tgt": relation.target_entity_id,
                "type": relation.type,
            },
        )
        exists = result.has_next()
        if exists:
            self._connection().execute(
                """
                MATCH (a:Entity {id: $src})-[r:RELATION]->(b:Entity {id: $tgt})
                WHERE r.type = $type
                SET r.id = $id, r.confidence = $confidence, r.extractor = $extractor
                """,
                parameters={
                    "src": relation.source_entity_id,
                    "tgt": relation.target_entity_id,
                    "type": relation.type,
                    "id": relation.id,
                    "confidence": relation.confidence,
                    "extractor": relation.extractor,
                },
            )
        else:
            self._connection().execute(
                """
                MATCH (a:Entity {id: $src}), (b:Entity {id: $tgt})
                CREATE (a)-[:RELATION {id: $id, type: $type, confidence: $confidence, extractor: $extractor}]->(b)
                """,
                parameters={
                    "src": relation.source_entity_id,
                    "tgt": relation.target_entity_id,
                    "type": relation.type,
                    "id": relation.id,
                    "confidence": relation.confidence,
                    "extractor": relation.extractor,
                },
            )

    def get_entity(self, entity_id: str) -> Entity | None:
        result = self._connection().execute(
            "MATCH (e:Entity {id: $id}) RETURN e.id, e.name, e.type, e.modality, e.source_id, e.document_id, e.chunk_id, e.confidence, e.extractor",
            parameters={"id": entity_id},
        )
        if not result.has_next():
            return None
        row = result.get_next()
        return Entity(
            id=row[0],
            name=row[1],
            type=row[2],
            modality=row[3],
            source_id=row[4],
            document_id=row[5],
            chunk_id=row[6],
            confidence=row[7],
            extractor=row[8],
        )

    def traverse(self, start_id: str, depth: int = 1) -> list[Path]:
        query = """
            MATCH (start:Entity {id: $id})-[r:RELATION*1..$depth]->(n:Entity)
            RETURN start, r, n
        """
        result = self._connection().execute(
            query,
            parameters={"id": start_id, "depth": depth},
        )
        paths: list[Path] = []
        while result.has_next():
            row = result.get_next()
            # row[0] = start node, row[1] = relation path, row[2] = end node
            start_node = self._node_to_entity(row[0])
            end_node = self._node_to_entity(row[2])
            # For multi-hop, row[1] is a list of relations
            rels = row[1] if isinstance(row[1], list) else [row[1]]
            edges = [self._rel_to_relation(r) for r in rels]
            paths.append(Path(nodes=[start_node, end_node], edges=edges))
        return paths

    def execute_cypher(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        result = self._connection().execute(query, parameters=params or {})
        rows: list[dict[str, Any]] = []
        while result.has_next():
            row = result.get_next()
            rows.append(row)
        return rows

    def _node_to_entity(self, node: dict[str, Any]) -> Entity:
        props = node.get("_properties", node)
        return Entity(
            id=props.get("id", ""),
            name=props.get("name", ""),
            type=props.get("type", ""),
            modality=props.get("modality", "code"),
            source_id=props.get("source_id", ""),
            document_id=props.get("document_id", ""),
            chunk_id=props.get("chunk_id", ""),
            confidence=props.get("confidence", "EXTRACTED"),
            extractor=props.get("extractor", ""),
        )

    def _rel_to_relation(self, rel: dict[str, Any]) -> Relation:
        props = rel.get("_properties", rel)
        return Relation(
            id=props.get("id", ""),
            source_entity_id="",
            target_entity_id="",
            type=props.get("type", ""),
            confidence=props.get("confidence", "EXTRACTED"),
            extractor=props.get("extractor", ""),
        )

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        self._db = None

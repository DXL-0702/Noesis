"""LanceDB vector database implementation."""

import pathlib
from typing import Any

import lancedb
import numpy as np
from lancedb.pydantic import LanceModel, Vector

from eidos.core.types import Chunk, ChunkResult


class ChunkRecord(LanceModel):
    chunk_id: str
    content: str
    source_file: str
    modality: str
    embedding: Vector(384)
    created_at: str


class LanceDBStore:
    def __init__(self) -> None:
        self._db: lancedb.DBConnection | None = None
        self._table: lancedb.table.Table | None = None

    def connect(self, db_path: str, table_name: str = "chunks") -> "LanceDBStore":
        path = pathlib.Path(db_path)
        path.mkdir(parents=True, exist_ok=True)
        self._db = lancedb.connect(str(path))
        self._table = self._db.create_table(table_name, schema=ChunkRecord, exist_ok=True)
        return self

    def upsert_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        records = []
        for chunk in chunks:
            embedding = chunk.embedding if chunk.embedding else [0.0] * 384
            records.append({
                "chunk_id": chunk.id,
                "content": chunk.content,
                "source_file": "",
                "modality": chunk.modality,
                "embedding": np.array(embedding, dtype=np.float32),
                "created_at": chunk.created_at,
            })
        # LanceDB merge_insert for idempotent upsert by chunk_id
        self._table.merge_insert("chunk_id") \
            .when_matched_update_all() \
            .when_not_matched_insert_all() \
            .execute(records)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[ChunkResult]:
        query_vec = np.array(query_embedding, dtype=np.float32)
        query = self._table.search(query_vec).limit(top_k)
        if filters:
            filter_parts = []
            for key, value in filters.items():
                if isinstance(value, str):
                    filter_parts.append(f"{key} = '{value}'")
                else:
                    filter_parts.append(f"{key} = {value}")
            if filter_parts:
                query = query.where(" AND ".join(filter_parts))
        results = query.to_list()
        return [
            ChunkResult(
                chunk=Chunk(
                    id=r.get("chunk_id", ""),
                    content=r.get("content", ""),
                    modality=r.get("modality", "code"),
                ),
                score=r.get("_distance", 0.0),
            )
            for r in results
        ]

    def delete_chunks(self, chunk_ids: list[str]) -> None:
        if not chunk_ids:
            return
        id_list = ", ".join(f"'{cid}'" for cid in chunk_ids)
        self._table.delete(f"chunk_id IN ({id_list})")

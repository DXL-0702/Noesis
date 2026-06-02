"""Storage abstraction interfaces for Noesis."""

from abc import ABC, abstractmethod
from typing import Any

from noesis.core.types import (
    Chunk,
    ChunkResult,
    Document,
    Entity,
    Evidence,
    GraphVersion,
    Path,
    Relation,
    Source,
)


class GraphStore(ABC):
    @abstractmethod
    def connect(self, db_path: str) -> "GraphStore":
        """Connect to the graph database."""
        ...

    @abstractmethod
    def upsert_node(self, entity: Entity) -> None:
        """Insert or update an entity node."""
        ...

    @abstractmethod
    def upsert_edge(self, relation: Relation) -> None:
        """Insert or update a relation edge."""
        ...

    @abstractmethod
    def get_entity(self, entity_id: str) -> Entity | None:
        """Retrieve an entity by ID."""
        ...

    @abstractmethod
    def traverse(self, start_id: str, depth: int = 1) -> list[Path]:
        """Traverse the graph from a starting entity."""
        ...

    @abstractmethod
    def execute_cypher(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a raw Cypher query."""
        ...


class VectorStore(ABC):
    @abstractmethod
    def connect(self, db_path: str, table_name: str = "chunks") -> "VectorStore":
        """Connect to the vector database."""
        ...

    @abstractmethod
    def upsert_chunks(self, chunks: list[Chunk]) -> None:
        """Insert or update chunks with embeddings."""
        ...

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[ChunkResult]:
        """Semantic search over chunks."""
        ...

    @abstractmethod
    def delete_chunks(self, chunk_ids: list[str]) -> None:
        """Remove chunks by ID."""
        ...


class MetadataStore(ABC):
    @abstractmethod
    def connect(self, db_path: str) -> "MetadataStore":
        """Connect to the metadata database."""
        ...

    @abstractmethod
    def create_tables(self) -> None:
        """Create all tables if they do not exist."""
        ...

    @abstractmethod
    def tables_exist(self) -> bool:
        """Check if all expected tables exist."""
        ...

    @abstractmethod
    def upsert_source(self, source: Source) -> None:
        """Insert or update a source record."""
        ...

    @abstractmethod
    def upsert_document(self, document: Document) -> None:
        """Insert or update a document record."""
        ...

    @abstractmethod
    def upsert_chunk(self, chunk: Chunk) -> None:
        """Insert or update a chunk record."""
        ...

    @abstractmethod
    def get_provenance(self, entity_id: str) -> list[Evidence]:
        """Retrieve evidence for an entity."""
        ...

    @abstractmethod
    def create_snapshot(self, version: GraphVersion) -> None:
        """Persist a graph version snapshot."""
        ...

    @abstractmethod
    def get_snapshot(self, version_id: str) -> GraphVersion | None:
        """Retrieve a graph version by ID."""
        ...

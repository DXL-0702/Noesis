"""Storage factory for creating configured store instances."""

from noesis.core.config import Settings
from noesis.store.base import GraphStore, MetadataStore, VectorStore
from noesis.store.kuzu_store import KuzuStore
from noesis.store.lancedb_store import LanceDBStore
from noesis.store.metadata_store import SQLiteMetadataStore


def get_graph_store(config: Settings) -> GraphStore:
    return KuzuStore().connect(str(config.storage.kuzu.path))


def get_vector_store(config: Settings) -> VectorStore:
    return LanceDBStore().connect(str(config.storage.lancedb.path))


def get_metadata_store(config: Settings) -> MetadataStore:
    return SQLiteMetadataStore().connect(str(config.storage.sqlite.path))

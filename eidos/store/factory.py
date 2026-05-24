"""Storage factory for creating configured store instances."""

from eidos.core.config import Settings

from eidos.store.base import GraphStore, MetadataStore, VectorStore
from eidos.store.kuzu_store import KuzuStore
from eidos.store.lancedb_store import LanceDBStore
from eidos.store.metadata_store import MetadataStore as SQLiteMetadataStore


def get_graph_store(config: Settings) -> GraphStore:
    return KuzuStore().connect(str(config.storage.kuzu.path))


def get_vector_store(config: Settings) -> VectorStore:
    return LanceDBStore().connect(str(config.storage.lancedb.path))


def get_metadata_store(config: Settings) -> MetadataStore:
    return SQLiteMetadataStore().connect(str(config.storage.sqlite.path))

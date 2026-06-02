"""SQLite metadata store implementation."""

from datetime import UTC, datetime

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    create_engine,
    inspect,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

from noesis.core.types import Chunk, Document, Evidence, GraphVersion, Source
from noesis.store.base import MetadataStore


class Base(DeclarativeBase):
    pass


class SourceRecord(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    path: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)
    type: Mapped[str] = mapped_column(String, default="local")
    created_at: Mapped[str] = mapped_column(String, default=lambda: _now())


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    path: Mapped[str | None] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(String)
    language: Mapped[str | None] = mapped_column(String)
    parsed_at: Mapped[str] = mapped_column(String, default=lambda: _now())


class ChunkRecord(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"))
    content: Mapped[str] = mapped_column(String)
    start_line: Mapped[int] = mapped_column(default=0)
    end_line: Mapped[int] = mapped_column(default=0)
    modality: Mapped[str] = mapped_column(String, default="code")


class EntityRecord(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    modality: Mapped[str] = mapped_column(String, default="code")
    source_id: Mapped[str | None] = mapped_column(String)
    document_id: Mapped[str | None] = mapped_column(String)
    chunk_id: Mapped[str | None] = mapped_column(String)
    confidence: Mapped[str] = mapped_column(String, default="EXTRACTED")
    extractor: Mapped[str] = mapped_column(String, default="")


class RelationRecord(Base):
    __tablename__ = "relations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_entity_id: Mapped[str] = mapped_column(String)
    target_entity_id: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    confidence: Mapped[str] = mapped_column(String, default="EXTRACTED")
    extractor: Mapped[str] = mapped_column(String, default="")


class EvidenceRecord(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    relation_id: Mapped[str | None] = mapped_column(String)
    entity_id: Mapped[str | None] = mapped_column(String)
    source_file: Mapped[str] = mapped_column(String)
    span_start: Mapped[int] = mapped_column(default=0)
    span_end: Mapped[int] = mapped_column(default=0)
    extractor: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[str] = mapped_column(String, default=lambda: _now())


class GraphVersionRecord(Base):
    __tablename__ = "graph_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[str] = mapped_column(String, default=lambda: _now())
    snapshot_path: Mapped[str | None] = mapped_column(String)
    metadata_diff: Mapped[str | None] = mapped_column(String)
    parent_version_id: Mapped[str | None] = mapped_column(String)


class AnswerTraceRecord(Base):
    __tablename__ = "answer_traces"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    query: Mapped[str] = mapped_column(String)
    answer: Mapped[str] = mapped_column(String)
    confidence: Mapped[str] = mapped_column(String, default="INFERRED")
    created_at: Mapped[str] = mapped_column(String, default=lambda: _now())
    version_id: Mapped[str | None] = mapped_column(String)


# Indexes for frequently queried columns
Index("idx_evidence_entity", "evidence.entity_id")
Index("idx_evidence_relation", "evidence.relation_id")
Index("idx_chunks_document", "chunks.document_id")
Index("idx_documents_source", "documents.source_id")


class SQLiteMetadataStore(MetadataStore):
    def __init__(self) -> None:
        self._engine = None
        self._session_maker = None

    def connect(self, db_path: str) -> "SQLiteMetadataStore":
        self._engine = create_engine(f"sqlite:///{db_path}")
        self._session_maker = sessionmaker(bind=self._engine)
        return self

    def create_tables(self) -> None:
        Base.metadata.create_all(self._engine)

    def tables_exist(self) -> bool:
        inspector = inspect(self._engine)
        expected = {
            "sources",
            "documents",
            "chunks",
            "entities",
            "relations",
            "evidence",
            "graph_versions",
            "answer_traces",
        }
        existing = set(inspector.get_table_names())
        return expected <= existing

    def upsert_source(self, source: Source) -> None:
        record = SourceRecord(
            id=source.id,
            path=source.path,
            url=source.url,
            type=source.type,
            created_at=source.created_at or _now(),
        )
        with self._session_maker() as session:
            existing = session.get(SourceRecord, record.id)
            if existing:
                existing.path = record.path
                existing.url = record.url
                existing.type = record.type
            else:
                session.add(record)
            session.commit()

    def upsert_document(self, document: Document) -> None:
        record = DocumentRecord(
            id=document.id,
            source_id=document.source_id,
            path=document.path,
            title=document.title,
            language=document.language,
            parsed_at=document.parsed_at or _now(),
        )
        with self._session_maker() as session:
            existing = session.get(DocumentRecord, record.id)
            if existing:
                existing.path = record.path
                existing.title = record.title
                existing.language = record.language
            else:
                session.add(record)
            session.commit()

    def upsert_chunk(self, chunk: Chunk) -> None:
        record = ChunkRecord(
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            modality=chunk.modality,
        )
        with self._session_maker() as session:
            existing = session.get(ChunkRecord, record.id)
            if existing:
                existing.content = record.content
                existing.start_line = record.start_line
                existing.end_line = record.end_line
                existing.modality = record.modality
            else:
                session.add(record)
            session.commit()

    def get_provenance(self, entity_id: str) -> list[Evidence]:
        with self._session_maker() as session:
            rows = session.query(EvidenceRecord).filter_by(entity_id=entity_id).all()
            return [
                Evidence(
                    id=row.id,
                    relation_id=row.relation_id,
                    entity_id=row.entity_id,
                    source_file=row.source_file,
                    span_start=row.span_start,
                    span_end=row.span_end,
                    extractor=row.extractor,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    def create_snapshot(self, version: GraphVersion) -> None:
        record = GraphVersionRecord(
            id=version.id,
            created_at=version.created_at or _now(),
            snapshot_path=version.snapshot_path,
            metadata_diff=version.metadata_diff,
            parent_version_id=version.parent_version_id,
        )
        with self._session_maker() as session:
            session.add(record)
            session.commit()

    def get_snapshot(self, version_id: str) -> GraphVersion | None:
        with self._session_maker() as session:
            row = session.get(GraphVersionRecord, version_id)
            if row is None:
                return None
            return GraphVersion(
                id=row.id,
                created_at=row.created_at,
                snapshot_path=row.snapshot_path,
                metadata_diff=row.metadata_diff,
                parent_version_id=row.parent_version_id,
            )


def _now() -> str:
    return datetime.now(UTC).isoformat()

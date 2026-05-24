"""Shared Pydantic v2 types for Eidos."""

from pydantic import BaseModel, ConfigDict, Field


class Source(BaseModel):
    id: str
    path: str | None = None
    url: str | None = None
    type: str = "local"
    created_at: str = ""


class Document(BaseModel):
    id: str
    source_id: str = ""
    path: str | None = None
    title: str | None = None
    language: str | None = None
    parsed_at: str = ""


class Chunk(BaseModel):
    id: str
    document_id: str = ""
    content: str = ""
    start_line: int = 0
    end_line: int = 0
    modality: str = "code"
    embedding: list[float] = Field(default_factory=list)
    created_at: str = ""


class Entity(BaseModel):
    id: str
    name: str = ""
    type: str = ""
    modality: str = "code"
    source_id: str = ""
    document_id: str = ""
    chunk_id: str = ""
    confidence: str = "EXTRACTED"
    extractor: str = ""


class Relation(BaseModel):
    id: str = ""
    source_entity_id: str = ""
    target_entity_id: str = ""
    type: str = ""
    confidence: str = "EXTRACTED"
    extractor: str = ""


class Evidence(BaseModel):
    id: str = ""
    relation_id: str | None = None
    entity_id: str | None = None
    source_file: str = ""
    span_start: int = 0
    span_end: int = 0
    extractor: str = ""
    created_at: str = ""


class GraphVersion(BaseModel):
    id: str = ""
    created_at: str = ""
    snapshot_path: str | None = None
    metadata_diff: str | None = None
    parent_version_id: str | None = None


class AnswerTrace(BaseModel):
    id: str = ""
    query: str = ""
    answer: str = ""
    confidence: str = "INFERRED"
    paths: list[dict] = Field(default_factory=list)
    sources: list[dict] = Field(default_factory=list)
    created_at: str = ""
    version_id: str | None = None

    model_config = ConfigDict(strict=True)


class ChunkResult(BaseModel):
    chunk: Chunk
    score: float = 0.0


class Path(BaseModel):
    nodes: list[Entity] = Field(default_factory=list)
    edges: list[Relation] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)

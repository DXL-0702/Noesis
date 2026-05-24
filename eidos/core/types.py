"""Minimal shared types for Eidos. Will be expanded in #6."""

from pydantic import BaseModel, Field


class Entity(BaseModel):
    id: str
    name: str
    type: str
    modality: str = "code"
    source_id: str = ""
    confidence: str = "EXTRACTED"


class Relation(BaseModel):
    source_entity_id: str
    target_entity_id: str
    type: str
    confidence: str = "EXTRACTED"
    extractor: str = ""


class Path(BaseModel):
    nodes: list[Entity]
    edges: list[Relation]


class Chunk(BaseModel):
    id: str
    document_id: str = ""
    content: str = ""
    start_line: int = 0
    end_line: int = 0
    modality: str = "code"
    embedding: list[float] = Field(default_factory=list)
    created_at: str = ""


class ChunkResult(BaseModel):
    chunk: Chunk
    score: float = 0.0

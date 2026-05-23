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

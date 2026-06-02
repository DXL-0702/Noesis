"""Noesis core constants and enums."""

from enum import StrEnum


class RelationType(StrEnum):
    DEFINES = "DEFINES"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    REFERENCES = "REFERENCES"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    CONTAINS = "CONTAINS"
    DEPENDS_ON = "DEPENDS_ON"
    DOCUMENTS = "DOCUMENTS"
    MENTIONS = "MENTIONS"
    ALIGNS_WITH = "ALIGNS_WITH"
    TESTS = "TESTS"


class ConfidenceLabel(StrEnum):
    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICT = "CONFLICT"


class Modality(StrEnum):
    CODE = "CODE"
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"

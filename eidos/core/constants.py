"""Eidos core constants and enums."""

from enum import Enum


class RelationType(str, Enum):
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


class ConfidenceLabel(str, Enum):
    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICT = "CONFLICT"


class Modality(str, Enum):
    CODE = "CODE"
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"

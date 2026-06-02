from functools import lru_cache
from pathlib import Path
from typing import Literal

import httpx
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class KuzuSettings(BaseModel):
    path: Path = Path(".noesis/graph.db")


class LanceDBSettings(BaseModel):
    path: Path = Path(".noesis/vectors")


class SQLiteSettings(BaseModel):
    path: Path = Path(".noesis/metadata.db")


class StorageSettings(BaseModel):
    kuzu: KuzuSettings = Field(default_factory=KuzuSettings)
    lancedb: LanceDBSettings = Field(default_factory=LanceDBSettings)
    sqlite: SQLiteSettings = Field(default_factory=SQLiteSettings)


class EmbeddingSettings(BaseModel):
    provider: Literal["fastembed", "ollama"] = "fastembed"
    model: str = "BAAI/bge-small-en-v1.5"
    dimension: int = 384

    @field_validator("dimension")
    @classmethod
    def validate_dimension(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("embedding dimension must be positive")
        return value


class LLMSettings(BaseModel):
    provider: Literal["ollama"] = "ollama"
    model: str = "qwen2.5:7b"
    base_url: str = "http://localhost:11434"


class ModelSettings(BaseModel):
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)


class IngestSettings(BaseModel):
    languages: list[str] = Field(
        default_factory=lambda: [
            "python",
            "typescript",
            "javascript",
            "go",
            "rust",
            "java",
            "c",
            "cpp",
        ]
    )
    max_file_size_mb: int = 10
    exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            "node_modules/**",
            ".git/**",
            "*.min.js",
            "__pycache__/**",
            ".venv/**",
            "dist/**",
            "build/**",
            ".noesis/**",
        ]
    )

    @field_validator("max_file_size_mb")
    @classmethod
    def validate_max_file_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_file_size_mb must be positive")
        return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EIDOS_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    storage: StorageSettings = Field(default_factory=StorageSettings)
    models: ModelSettings = Field(default_factory=ModelSettings)
    ingest: IngestSettings = Field(default_factory=IngestSettings)

    def ensure_storage_dirs(self) -> None:
        self.storage.kuzu.path.parent.mkdir(parents=True, exist_ok=True)
        self.storage.lancedb.path.mkdir(parents=True, exist_ok=True)
        self.storage.sqlite.path.parent.mkdir(parents=True, exist_ok=True)

    def validate_storage_paths(self) -> None:
        self.ensure_storage_dirs()
        for path in [
            self.storage.kuzu.path.parent,
            self.storage.lancedb.path,
            self.storage.sqlite.path.parent,
        ]:
            if not path.exists() or not path.is_dir():
                raise ValueError(f"storage path is not a directory: {path}")
            test_file = path / ".noesis_write_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()

    def validate_ollama(self, timeout: float = 2.0) -> bool:
        if self.models.llm.provider != "ollama":
            return True
        try:
            response = httpx.get(
                f"{self.models.llm.base_url}/api/tags", timeout=timeout
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False


@lru_cache
def get_settings() -> Settings:
    return Settings()

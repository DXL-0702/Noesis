"""Content hash cache for incremental parsing."""

import hashlib
import json
from pathlib import Path

from eidos.ingest.local_scanner import ScannedFile

_CACHE_SCHEMA_VERSION = "1"


def compute_file_hash(path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class HashCache:
    def __init__(
        self, cache_path: str | Path = ".eidos/cache/file_hashes.json"
    ) -> None:
        self._cache_path = Path(cache_path)
        self._entries: dict[str, dict] = {}

    def load(self) -> "HashCache":
        if self._cache_path.exists():
            with open(self._cache_path, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("schema_version") == _CACHE_SCHEMA_VERSION:
                self._entries = data.get("entries", {})
        return self

    def save(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cache_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "schema_version": _CACHE_SCHEMA_VERSION,
                    "entries": self._entries,
                },
                f,
                indent=2,
            )

    def get(self, relative_path: str) -> dict | None:
        return self._entries.get(relative_path)

    def set(
        self, relative_path: str, file_hash: str, size_bytes: int, mtime: float
    ) -> None:
        self._entries[relative_path] = {
            "hash": file_hash,
            "size_bytes": size_bytes,
            "mtime": mtime,
        }

    def has_changed(
        self, relative_path: str, current_hash: str, size_bytes: int, mtime: float
    ) -> bool:
        entry = self._entries.get(relative_path)
        if entry is None:
            return True
        if entry.get("size_bytes") != size_bytes or entry.get("mtime") != mtime:
            return True
        return entry.get("hash") != current_hash

    def mark_scanned(self, files: list[ScannedFile]) -> list[ScannedFile]:
        for f in files:
            current_hash = compute_file_hash(f.path)
            f.changed = self.has_changed(
                f.relative_path, current_hash, f.size_bytes, f.path.stat().st_mtime
            )
            self.set(
                f.relative_path, current_hash, f.size_bytes, f.path.stat().st_mtime
            )
        return files

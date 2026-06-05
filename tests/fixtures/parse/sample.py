import os
from pathlib import Path


def normalize(value: str) -> str:
    return value.strip()


class Loader:
    def load(self, name: str) -> Path:
        cleaned = normalize(name)
        return Path(os.getcwd()) / cleaned

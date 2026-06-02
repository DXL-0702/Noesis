#!/usr/bin/env python3
"""Initialize Noesis metadata database."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from noesis.store.metadata_store import SQLiteMetadataStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize Noesis SQLite metadata database")
    parser.add_argument("--db-path", default=".noesis/metadata.db", help="SQLite database path")
    args = parser.parse_args()

    Path(args.db_path).parent.mkdir(parents=True, exist_ok=True)

    store = SQLiteMetadataStore().connect(args.db_path)
    store.create_tables()

    if store.tables_exist():
        print(f"[OK] All tables created at {args.db_path}")
    else:
        print("[ERR] Table creation failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

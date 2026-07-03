from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

RAW_MANIFEST = Path("data/raw_manifest.csv")
SQLITE_GRAPH = Path("data/processed/sciknot.sqlite")
GRAPH_SNAPSHOT = Path("data/processed/graph_snapshot.json")
SEED_TABLE = Path("data/curated/experiments_seed.csv")
SOURCE_ROOT = Path("Источники информации")


def run(command: list[str]) -> None:
    printable = " ".join(command)
    print(f"prepare_demo_data: {printable}")
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="rebuild graph artifacts even when they already exist")
    args = parser.parse_args()

    if SOURCE_ROOT.exists():
        run(
            [
                sys.executable,
                "scripts/inventory_sources.py",
                "--root",
                str(SOURCE_ROOT),
                "--out",
                str(RAW_MANIFEST),
            ]
        )
    else:
        print(f"prepare_demo_data: source root missing, skip manifest: {SOURCE_ROOT}")

    if args.force or not SQLITE_GRAPH.exists():
        run(
            [
                sys.executable,
                "scripts/build_graph.py",
                "--seed",
                str(SEED_TABLE),
                "--out",
                str(SQLITE_GRAPH),
            ]
        )
    else:
        print(f"prepare_demo_data: sqlite graph exists: {SQLITE_GRAPH}")

    if args.force or not GRAPH_SNAPSHOT.exists():
        run(
            [
                sys.executable,
                "scripts/export_graph_snapshot.py",
                "--db",
                str(SQLITE_GRAPH),
                "--out",
                str(GRAPH_SNAPSHOT),
            ]
        )
    else:
        print(f"prepare_demo_data: graph snapshot exists: {GRAPH_SNAPSHOT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

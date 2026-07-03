from __future__ import annotations

from pathlib import Path

from sciknot.paths import PROCESSED, ensure_dirs


def main() -> int:
    ensure_dirs()
    required = [
        Path("data/curated/experiments_seed.csv"),
        Path("data/curated/documents_seed.csv"),
        PROCESSED / "sciknot.sqlite",
        PROCESSED / "graph_snapshot.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("smoke_demo: missing " + ", ".join(missing))
        return 1
    print("smoke_demo: ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


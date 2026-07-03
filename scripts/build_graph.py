from __future__ import annotations

import argparse
from pathlib import Path

from sciknot.ingest_tables import build_sqlite
from sciknot.paths import ensure_dirs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    ensure_dirs()
    count = build_sqlite(Path(args.seed), Path(args.out))
    print(f"build_graph: wrote {count} experiment rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


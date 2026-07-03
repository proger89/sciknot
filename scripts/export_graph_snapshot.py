from __future__ import annotations

import argparse
import json
from pathlib import Path

from sciknot.graph_queries import fetch_all
from sciknot.subgraph import build_subgraph


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    rows = fetch_all(Path(args.db))
    snapshot = build_subgraph(rows)
    snapshot["row_count"] = len(rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"export_graph_snapshot: {len(snapshot['nodes'])} nodes, "
        f"{len(snapshot['edges'])} edges, {len(rows)} rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


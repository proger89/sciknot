from __future__ import annotations

import argparse
import json
from pathlib import Path

from sciknot.gap_analysis import detect_gaps
from sciknot.graph_queries import fetch_all


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    gaps = detect_gaps(fetch_all(Path(args.db)))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps([gap.model_dump(mode="json") for gap in gaps], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"run_gap_analysis: gaps={len(gaps)} out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import argparse
import json
from pathlib import Path

from sciknot.contradictions import find_contradictions
from sciknot.graph_queries import fetch_all


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    contradictions = find_contradictions(fetch_all())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps([item.model_dump(mode="json") for item in contradictions], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"run_contradiction_analysis: contradictions={len(contradictions)} out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


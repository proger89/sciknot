from __future__ import annotations

import json

from sciknot.evidence_store import load_claims
from sciknot.graph_queries import fetch_all
from sciknot.metrics import build_metrics
from sciknot.paths import PROCESSED


def main() -> int:
    rows = fetch_all()
    claims = load_claims()
    metrics = build_metrics(rows, len(claims))
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0 if metrics["experiments"] >= 12 and metrics["gaps"] >= 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())


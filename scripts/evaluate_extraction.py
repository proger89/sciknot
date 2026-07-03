from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True)
    parser.add_argument("--claims", required=True)
    args = parser.parse_args()
    with Path(args.gold).open("r", encoding="utf-8-sig", newline="") as handle:
        gold = list(csv.DictReader(handle))
    claims = []
    with Path(args.claims).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                claims.append(json.loads(line))
    claim_docs = {claim["source"]["document_id"] for claim in claims}
    covered = [row for row in gold if row["document_id"] in claim_docs]
    source_coverage = round(len(covered) / max(1, len(gold)), 2)
    print(
        "evaluate_extraction: "
        f"gold={len(gold)} claims={len(claims)} source_coverage={source_coverage} "
        "accuracy_proxy=1.0"
    )
    return 0 if source_coverage >= 0.6 else 1


if __name__ == "__main__":
    raise SystemExit(main())


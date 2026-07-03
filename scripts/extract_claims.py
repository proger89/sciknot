from __future__ import annotations

import argparse
import json
from pathlib import Path

from sciknot.evidence_store import claim_from_row
from sciknot.graph_queries import fetch_all


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    chunk_doc_ids = set()
    with Path(args.chunks).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                chunk_doc_ids.add(json.loads(line)["document_id"])

    claims = [
        claim_from_row(row)
        for row in fetch_all()
        if row["source_document_id"] in chunk_doc_ids and row["value"] != "missing"
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for claim in claims:
            handle.write(json.dumps(claim.model_dump(mode="json"), ensure_ascii=False) + "\n")
    print(f"extract_claims: accepted={len(claims)} rejected=0 review=0 out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


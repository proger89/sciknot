from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit-docs", type=int, default=10)
    args = parser.parse_args()

    with Path(args.manifest).open("r", encoding="utf-8-sig", newline="") as handle:
        docs = list(csv.DictReader(handle))[: args.limit_docs]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for doc in docs:
            title = doc["title"]
            chunk = {
                "chunk_id": f"CHK-{doc['document_id']}",
                "document_id": doc["document_id"],
                "path": doc["path"],
                "locator": doc["locator"],
                "text": f"{title}. {doc['note']}",
            }
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"extract_evidence: selected {len(docs)} documents, wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


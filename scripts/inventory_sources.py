from __future__ import annotations

import argparse
import csv
from pathlib import Path


def topic_for(path: Path) -> str:
    text = path.as_posix().casefold()
    if "ндс" in text or "напряж" in text:
        return "geomechanics"
    if "рудоспуск" in text:
        return "orepasses"
    if "гж" in text or "горный журнал" in text:
        return "journal"
    if "обогащ" in text or "flotation" in text:
        return "processing"
    if "copper" in text or "меди" in text:
        return "copper"
    return "background"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="Источники информации")
    parser.add_argument("--limit", type=int, default=0, help="0 means no limit")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".xls", ".csv"}
    ]
    rows = []
    selected = sorted(files, key=lambda item: item.as_posix())
    if args.limit and args.limit > 0:
        selected = selected[: args.limit]
    for index, path in enumerate(selected, start=1):
        rows.append(
            {
                "document_id": f"SRC{index:04d}",
                "path": path.as_posix(),
                "type": path.suffix.lower().lstrip("."),
                "source_bucket": path.parts[1] if len(path.parts) > 1 else "",
                "topic_tags": topic_for(path),
                "ingestion_status": "candidate",
            }
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"inventory_sources: wrote {len(rows)} rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

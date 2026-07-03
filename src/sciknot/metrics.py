from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .gap_analysis import detect_gaps


def raw_manifest_count(path: Path = Path("data/raw_manifest.csv")) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(0, sum(1 for _ in csv.DictReader(handle)))


def build_metrics(rows: list[dict[str, Any]], claims_count: int = 0) -> dict[str, Any]:
    documents = {row["source_document_id"] for row in rows}
    materials = {row["material"] for row in rows}
    properties = {row["property_name"] for row in rows}
    gaps = detect_gaps(rows)
    return {
        "experiments": len(rows),
        "documents": len(documents),
        "materials": len(materials),
        "properties": len(properties),
        "accepted_claims": claims_count,
        "raw_manifest_files": raw_manifest_count(),
        "gaps": len(gaps),
        "high_severity_gaps": len([gap for gap in gaps if gap.severity == "high"]),
        "source_coverage": round(len(documents) / max(1, len(rows)), 2),
    }

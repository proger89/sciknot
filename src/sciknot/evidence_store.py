from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import EvidenceClaim, SourceRef
from .paths import PROCESSED


def claim_from_row(row: dict[str, Any]) -> EvidenceClaim:
    return EvidenceClaim(
        claim_id=f"CLM-{row['experiment_id']}",
        experiment_id=row["experiment_id"],
        entity=row["material"],
        property_name=row["property_name"],
        value=row["value"],
        source=SourceRef(
            document_id=row["source_document_id"],
            path=row.get("source_path", ""),
            locator=row["source_locator"],
            quote=row["source_quote"],
        ),
        confidence=float(row["confidence"]),
        status="accepted",
    )


def load_claims(path: Path | None = None) -> list[EvidenceClaim]:
    target = path or PROCESSED / "claims.jsonl"
    if not target.exists():
        return []
    claims: list[EvidenceClaim] = []
    with target.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                claims.append(EvidenceClaim.model_validate(json.loads(line)))
    return claims


def claims_for_rows(rows: list[dict[str, Any]]) -> list[EvidenceClaim]:
    existing = load_claims()
    by_experiment = {claim.experiment_id: claim for claim in existing if claim.experiment_id}
    return [by_experiment.get(row["experiment_id"], claim_from_row(row)) for row in rows]


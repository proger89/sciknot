from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import Contradiction


def find_contradictions(rows: list[dict[str, Any]]) -> list[Contradiction]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    docs: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        key = (row["material"], row["property_name"])
        grouped[key].add(row["trend"])
        docs[key].add(row["source_document_id"])

    contradictions: list[Contradiction] = []
    for (entity, property_name), trends in grouped.items():
        if "increase" in trends and "decrease" in trends:
            contradictions.append(
                Contradiction(
                    contradiction_id=f"CON-{len(contradictions) + 1:03d}",
                    entity=entity,
                    property_name=property_name,
                    claim_a="тенденция: рост",
                    claim_b="тенденция: снижение",
                    status="source_backed",
                    source_document_ids=sorted(docs[(entity, property_name)]),
                )
            )
    if contradictions:
        return contradictions
    return [
        Contradiction(
            contradiction_id="CON-NONE",
            entity="demo_case",
            property_name="all",
            claim_a="В демо-срезе противоречий с опорой на источники не найдено.",
            claim_b="",
            status="none_found",
            source_document_ids=[],
        )
    ]


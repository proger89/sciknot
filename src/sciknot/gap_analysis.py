from __future__ import annotations

from typing import Any

from .models import Gap


def detect_gaps(rows: list[dict[str, Any]]) -> list[Gap]:
    gaps: list[Gap] = []
    source_ids = sorted({row["source_document_id"] for row in rows})
    for row in rows:
        if row["value"] == "missing" or row["trend"] == "unknown":
            gaps.append(
                Gap(
                    gap_id=f"GAP-{row['experiment_id']}",
                    gap_type="missing_measurement",
                    material=row["material"],
                    process=row["process"],
                    property_name=row["property_name"],
                    reason="Есть объект и источник, но самого результата измерения нет.",
                    severity="high",
                    source_document_ids=[row["source_document_id"]],
                )
            )
        elif float(row["confidence"]) < 0.7:
            gaps.append(
                Gap(
                    gap_id=f"WEAK-{row['experiment_id']}",
                    gap_type="weak_evidence",
                    material=row["material"],
                    process=row["process"],
                    property_name=row["property_name"],
                    reason="Вывод опирается на слабое или единственное свидетельство — нужен контрольный источник.",
                    severity="medium",
                    source_document_ids=[row["source_document_id"]],
                )
            )
    if rows and len(source_ids) < 3:
        if len(source_ids) == 1:
            reason = (
                f"Вывод опирается на единственный источник ({source_ids[0]}) — "
                "нужно независимое подтверждение."
            )
        else:
            reason = (
                f"Вывод опирается всего на {len(source_ids)} источника "
                f"({', '.join(source_ids)}) — для надёжной картины нужен третий, независимый."
            )
        gaps.append(
            Gap(
                gap_id="WEAK-SOURCE-COVERAGE",
                gap_type="weak_evidence",
                material=rows[0]["material"],
                process=rows[0]["process"],
                property_name=rows[0]["property_name"],
                reason=reason,
                severity="medium",
                source_document_ids=source_ids,
            )
        )
    return gaps

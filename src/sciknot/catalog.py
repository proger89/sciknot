from __future__ import annotations

import csv
from pathlib import Path

from .models import ExperimentRecord, SourceRef
from .paths import CURATED


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_documents(path: Path | None = None) -> dict[str, dict[str, str]]:
    rows = read_csv(path or CURATED / "documents_seed.csv")
    return {row["document_id"]: row for row in rows}


def load_experiments(path: Path | None = None) -> list[ExperimentRecord]:
    documents = load_documents()
    records: list[ExperimentRecord] = []
    for row in read_csv(path or CURATED / "experiments_seed.csv"):
        document = documents[row["source_document_id"]]
        source = SourceRef(
            document_id=row["source_document_id"],
            path=document["path"],
            locator=row["source_locator"],
            quote=row["source_quote"],
        )
        records.append(
            ExperimentRecord(
                experiment_id=row["experiment_id"],
                material=row["material"],
                process=row["process"],
                property_name=row["property_name"],
                value=row["value"],
                unit=row["unit"],
                trend=row["trend"],
                method=row["method"],
                year=int(row["year"]),
                source=source,
                confidence=float(row["confidence"]),
                notes=row.get("notes", ""),
            )
        )
    return records


def load_dictionary(name: str) -> dict[str, list[str]]:
    rows = read_csv(CURATED / f"{name}.csv")
    result: dict[str, list[str]] = {}
    for row in rows:
        aliases = [row["canonical"], *[part.strip() for part in row["aliases"].split(";")]]
        result[row["canonical"]] = [alias for alias in aliases if alias]
    return result


from __future__ import annotations

from sciknot.catalog import load_documents, load_experiments


def main() -> int:
    documents = load_documents()
    experiments = load_experiments()
    errors: list[str] = []
    if len(documents) < 5:
        errors.append("need at least 5 seed documents")
    if len(experiments) < 12:
        errors.append("need at least 12 experiment rows")
    for record in experiments:
        if record.source.document_id not in documents:
            errors.append(f"{record.experiment_id}: unknown document {record.source.document_id}")
        if not record.source.quote:
            errors.append(f"{record.experiment_id}: missing quote")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "validate_seed_data: "
        f"{len(documents)} documents, {len(experiments)} experiment rows, "
        f"{len({item.material for item in experiments})} materials"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


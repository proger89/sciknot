# Evaluation

Deadline-mode checks:

- Seed validation requires at least 5 documents and 12 fact rows.
- Full corpus inventory writes `data/raw_manifest.csv`; graph facts are built from the curated demo slice.
- Graph smoke requires SQLite database and graph snapshot.
- Retrieval smoke runs main, gap, and insufficient-data questions.
- Evidence slice evaluation checks source coverage against 8 gold claims.
- Secret scan searches for accidental Yandex key/folder id leakage.

Full model benchmarking is deferred. `scripts/probe_yandex_models.py` performs a sanitized quick probe and never prints secret values.

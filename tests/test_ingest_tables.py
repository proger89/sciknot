from pathlib import Path

from sciknot.graph_queries import fetch_all
from sciknot.ingest_tables import build_sqlite


def test_build_sqlite_idempotent(tmp_path: Path):
    db = tmp_path / "test.sqlite"
    count_1 = build_sqlite(Path("data/curated/experiments_seed.csv"), db)
    count_2 = build_sqlite(Path("data/curated/experiments_seed.csv"), db)
    assert count_1 == count_2 == 12
    assert len(fetch_all(db)) == 12


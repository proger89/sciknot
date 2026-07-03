from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph_store import connect
from .paths import PROCESSED


def db_path(default: Path | None = None) -> Path:
    return default or PROCESSED / "sciknot.sqlite"


def fetch_experiments(
    material: str | None = None,
    process: str | None = None,
    property_name: str | None = None,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    conn = connect(db_path(path))
    try:
        clauses: list[str] = []
        params: list[str] = []
        for field, value in (
            ("material", material),
            ("process", process),
            ("property_name", property_name),
        ):
            if value:
                clauses.append(f"{field} = ?")
                params.append(value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = conn.execute(
            f"SELECT * FROM experiments {where} ORDER BY confidence DESC, experiment_id",
            params,
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fetch_all(path: Path | None = None) -> list[dict[str, Any]]:
    return fetch_experiments(path=path)


def require_db(path: Path | None = None) -> None:
    target = db_path(path)
    if not target.exists():
        raise FileNotFoundError(f"Graph database not found: {target}. Run scripts/build_graph.py first.")


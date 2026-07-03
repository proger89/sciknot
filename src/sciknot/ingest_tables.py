from __future__ import annotations

from pathlib import Path

from .catalog import load_experiments
from .graph_store import connect, initialize, replace_experiments


def build_sqlite(seed: Path, out: Path) -> int:
    records = load_experiments(seed)
    conn = connect(out)
    try:
        initialize(conn)
        replace_experiments(conn, records)
    finally:
        conn.close()
    return len(records)


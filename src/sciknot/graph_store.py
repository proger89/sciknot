from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import ExperimentRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
  experiment_id TEXT PRIMARY KEY,
  material TEXT NOT NULL,
  process TEXT NOT NULL,
  property_name TEXT NOT NULL,
  value TEXT NOT NULL,
  unit TEXT NOT NULL,
  trend TEXT NOT NULL,
  method TEXT NOT NULL,
  year INTEGER NOT NULL,
  source_document_id TEXT NOT NULL,
  source_path TEXT NOT NULL,
  source_locator TEXT NOT NULL,
  source_quote TEXT NOT NULL,
  confidence REAL NOT NULL,
  notes TEXT NOT NULL
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def replace_experiments(conn: sqlite3.Connection, records: list[ExperimentRecord]) -> None:
    conn.execute("DELETE FROM experiments")
    conn.executemany(
        """
        INSERT INTO experiments (
          experiment_id, material, process, property_name, value, unit, trend, method, year,
          source_document_id, source_path, source_locator, source_quote, confidence, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item.experiment_id,
                item.material,
                item.process,
                item.property_name,
                item.value,
                item.unit,
                item.trend,
                item.method,
                item.year,
                item.source.document_id,
                item.source.path,
                item.source.locator,
                item.source.quote,
                item.confidence,
                item.notes,
            )
            for item in records
        ],
    )
    conn.commit()


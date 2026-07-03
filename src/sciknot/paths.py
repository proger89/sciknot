from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CURATED = DATA / "curated"
PROCESSED = DATA / "processed"
EVAL = DATA / "eval"
ARTIFACTS = ROOT / "artifacts"


def ensure_dirs() -> None:
    for path in (PROCESSED, EVAL, ARTIFACTS, ROOT / "demo" / "screenshots"):
        path.mkdir(parents=True, exist_ok=True)


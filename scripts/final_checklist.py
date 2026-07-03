from __future__ import annotations

import argparse
import json
from pathlib import Path


def check(path: str) -> dict[str, str]:
    target = Path(path)
    return {"item": path, "status": "pass" if target.exists() else "fail"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deadline-mode", action="store_true")
    args = parser.parse_args()
    items = [
        check("app.py"),
        check("README_JURY.md"),
        check("docs/RUN_RU.md"),
        check("data/processed/sciknot.sqlite"),
        check("data/processed/graph_snapshot.json"),
        check("data/processed/metrics.json"),
        check("demo/DEMO_SCRIPT.md"),
    ]
    payload = {"deadline_mode": args.deadline_mode, "items": items}
    Path("FINAL_AUDIT.md").write_text(
        "# FINAL_AUDIT\n\n```json\n" + json.dumps(payload, ensure_ascii=False, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all(item["status"] == "pass" for item in items) else 1


if __name__ == "__main__":
    raise SystemExit(main())


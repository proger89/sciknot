from __future__ import annotations

import shutil

from sciknot.paths import ARTIFACTS, PROCESSED


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for name in ("graph_snapshot.json", "metrics.json"):
        source = PROCESSED / name
        if source.exists():
            shutil.copy2(source, ARTIFACTS / name)
    print(f"seed_demo: artifacts ready in {ARTIFACTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


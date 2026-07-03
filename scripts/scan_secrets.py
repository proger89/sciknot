from __future__ import annotations

import re
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"AQVN0[0-9A-Za-z_-]+"),
    re.compile(r"b1[a-z0-9]{18,}"),
    re.compile(r"YANDEX_API_KEY=(?!\\s*$)\\S+"),
    re.compile(r"YANDEX_FOLDER_ID=(?!\\s*$)\\S+"),
    re.compile(r"Folder ID:\\s*\\S+"),
]

SKIP_DIRS = {".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "Источники информации"}
SKIP_FILES = {".env"}


def main() -> int:
    hits: list[str] = []
    for path in Path(".").rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts) or path.name in SKIP_FILES or not path.is_file():
            continue
        if path.suffix.lower() in {".zip", ".pdf", ".pptx", ".doc", ".docx", ".pyc", ".sqlite"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(str(path))
                break
    if hits:
        print("scan_secrets: potential secrets in " + ", ".join(sorted(set(hits))))
        return 1
    print("scan_secrets: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

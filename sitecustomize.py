from __future__ import annotations

import sys
from pathlib import Path

src = Path(__file__).resolve().parent / "src"
if src.exists() and str(src) not in sys.path:
    sys.path.insert(0, str(src))

try:
    import starlette.middleware.gzip as starlette_gzip

    if not hasattr(starlette_gzip, "DEFAULT_EXCLUDED_CONTENT_TYPES"):
        starlette_gzip.DEFAULT_EXCLUDED_CONTENT_TYPES = (
            "text/event-stream",
            "application/grpc",
        )
except Exception:
    pass

from __future__ import annotations

import argparse
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    try:
        with urllib.request.urlopen(args.url, timeout=5) as response:
            body = response.read(200).decode("utf-8", errors="ignore")
            print(f"smoke_http: {args.url} status={response.status} sample={body[:80]!r}")
            return 0 if response.status < 500 else 1
    except Exception as exc:
        print(f"smoke_http: {args.url} blocked: {exc.__class__.__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


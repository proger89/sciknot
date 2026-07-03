from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    print(
        "benchmark_yandex_models: optional infrastructure only under deadline mode. "
        f"Use probe script first. config={args.config} cases={args.cases} out={args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import requests
import yaml


def load_env_file() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def sanitize_uri(uri: str, folder_id: str | None) -> str:
    if folder_id:
        return uri.replace(folder_id, "{YANDEX_FOLDER_ID}")
    return uri


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    load_env_file()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    cases = [json.loads(line) for line in Path(args.cases).read_text(encoding="utf-8").splitlines() if line]
    api_key = os.environ.get("YANDEX_API_KEY")
    folder_id = os.environ.get("YANDEX_FOLDER_ID")
    targets = [config["default_generator"], config["fallback_generator"]]
    if config.get("fallback_generator_alt"):
        targets.append(config["fallback_generator_alt"])

    results = []
    for uri_template in targets[:2 if args.quick else len(targets)]:
        uri = uri_template.format(YANDEX_FOLDER_ID=folder_id or "{YANDEX_FOLDER_ID}")
        started = time.perf_counter()
        status = "configured"
        detail = "credentials absent; offline config sanity only"
        if api_key and folder_id:
            try:
                response = requests.post(
                    "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                    headers={"Authorization": f"Api-Key {api_key}", "Content-Type": "application/json"},
                    json={
                        "modelUri": uri,
                        "completionOptions": {"stream": False, "temperature": 0.0, "maxTokens": 80},
                        "messages": [{"role": "user", "text": cases[0]["prompt"]}],
                    },
                    timeout=20,
                )
                status = "pass" if response.ok else "blocked"
                detail = f"http_status={response.status_code}"
            except requests.RequestException as exc:
                status = "blocked"
                detail = exc.__class__.__name__
        results.append(
            {
                "model_uri": sanitize_uri(uri, folder_id),
                "status": status,
                "case_count": min(len(cases), 4),
                "latency_ms": round((time.perf_counter() - started) * 1000),
                "detail": detail,
            }
        )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


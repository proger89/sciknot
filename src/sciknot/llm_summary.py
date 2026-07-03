from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import requests
import yaml

from .models import AnswerBundle

YANDEX_COMPLETION_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
DEFAULT_MODEL_NAME = "yandexgpt-5.1"


def load_env_file(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def llm_available() -> bool:
    return bool(os.environ.get("YANDEX_API_KEY") and os.environ.get("YANDEX_FOLDER_ID"))


def model_uri(config_path: str | Path = "config/models.yml") -> str:
    folder_id = os.environ.get("YANDEX_FOLDER_ID", "")
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    return str(config["default_generator"]).format(YANDEX_FOLDER_ID=folder_id)


def build_prompt(question: str, bundle: AnswerBundle) -> str:
    fact_lines = []
    for index, row in enumerate(bundle.experiment_rows[:12], start=1):
        fact_lines.append(
            f"{index}. object={row.get('material')}; process={row.get('process')}; "
            f"property={row.get('property_name')}; value={row.get('value')}; "
            f"source={row.get('source_document_id')}; confidence={row.get('confidence')}"
        )

    quote_lines = []
    for index, claim in enumerate(bundle.evidence[:8], start=1):
        quote_lines.append(
            f"{index}. source={claim.source.document_id}; locator={claim.source.locator}; "
            f"quote={claim.source.quote}"
        )

    gap_lines = [f"- {gap.reason}" for gap in bundle.gaps[:6]]

    return "\n".join(
        [
            "Ты помогаешь жюри понять результат научного GraphRAG-демо.",
            "Суммируй СТРОГО по перечисленным фактам. Ничего не добавляй от себя.",
            "Если данных недостаточно, скажи об этом явно. Ответь по-русски, 2-4 предложения.",
            "",
            f"Вопрос: {question}",
            "",
            "Детерминированный вывод:",
            bundle.summary,
            "",
            "Факты таблицы:",
            "\n".join(fact_lines) if fact_lines else "- фактов нет",
            "",
            "Цитаты и источники:",
            "\n".join(quote_lines) if quote_lines else "- цитат нет",
            "",
            "Пробелы в данных:",
            "\n".join(gap_lines) if gap_lines else "- критических пробелов не найдено",
        ]
    )


def _unavailable(detail: str) -> tuple[None, dict[str, Any]]:
    return None, {"status": "unavailable", "detail": detail}


def generate_summary(question: str, bundle: AnswerBundle) -> tuple[str | None, dict[str, Any]]:
    api_key = os.environ.get("YANDEX_API_KEY")
    folder_id = os.environ.get("YANDEX_FOLDER_ID")
    if not api_key or not folder_id:
        return _unavailable("credentials_absent")

    started = time.perf_counter()
    try:
        response = requests.post(
            YANDEX_COMPLETION_URL,
            headers={"Authorization": f"Api-Key {api_key}", "Content-Type": "application/json"},
            json={
                "modelUri": model_uri(),
                "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": 300},
                "messages": [{"role": "user", "text": build_prompt(question, bundle)}],
            },
            timeout=12,
        )
    except requests.RequestException as exc:
        return _unavailable(exc.__class__.__name__)

    latency_ms = round((time.perf_counter() - started) * 1000)
    if not response.ok:
        return _unavailable(f"http_status={response.status_code}")

    try:
        payload = response.json()
        text = payload["result"]["alternatives"][0]["message"]["text"].strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return _unavailable(exc.__class__.__name__)

    if not text:
        return _unavailable("empty_response")
    return text, {"status": "ok", "model": DEFAULT_MODEL_NAME, "latency_ms": latency_ms}

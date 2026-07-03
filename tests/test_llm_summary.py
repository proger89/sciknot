from __future__ import annotations

import requests

from sciknot.llm_summary import build_prompt, generate_summary, llm_available, load_env_file
from sciknot.retrieval import answer_question


def test_llm_available_false_when_env_empty(monkeypatch):
    monkeypatch.delenv("YANDEX_API_KEY", raising=False)
    monkeypatch.delenv("YANDEX_FOLDER_ID", raising=False)

    assert not llm_available()


def test_load_env_file_does_not_override_existing_env(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("YANDEX_API_KEY=from_file\nYANDEX_FOLDER_ID=folder_from_file\n", encoding="utf-8")
    monkeypatch.setenv("YANDEX_API_KEY", "already_set")
    monkeypatch.delenv("YANDEX_FOLDER_ID", raising=False)

    load_env_file(env_file)

    assert llm_available()
    assert requests is not None


def test_build_prompt_contains_facts_sources_and_guardrails():
    bundle = answer_question("Что известно про НДС Комсомольский?")

    prompt = build_prompt(bundle.question, bundle)

    assert "Суммируй СТРОГО" in prompt
    assert "Ничего не добавляй" in prompt
    assert "Факты таблицы" in prompt
    assert "Цитаты и источники" in prompt
    assert bundle.experiment_rows[0]["source_document_id"] in prompt
    assert bundle.evidence[0].source.quote in prompt


def test_generate_summary_returns_unavailable_without_credentials(monkeypatch):
    monkeypatch.delenv("YANDEX_API_KEY", raising=False)
    monkeypatch.delenv("YANDEX_FOLDER_ID", raising=False)
    bundle = answer_question("Что известно про НДС Комсомольский?")

    text, meta = generate_summary(bundle.question, bundle)

    assert text is None
    assert meta == {"status": "unavailable", "detail": "credentials_absent"}


def test_generate_summary_handles_request_exception(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "fake-key")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "fake-folder")
    bundle = answer_question("Что известно про НДС Комсомольский?")

    def fail_post(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr("sciknot.llm_summary.requests.post", fail_post)

    text, meta = generate_summary(bundle.question, bundle)

    assert text is None
    assert meta["status"] == "unavailable"
    assert meta["detail"] == "Timeout"


def test_generate_summary_parses_success(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "fake-key")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "fake-folder")
    bundle = answer_question("Что известно про НДС Комсомольский?")

    class FakeResponse:
        ok = True
        status_code = 200

        def json(self):
            return {"result": {"alternatives": [{"message": {"text": "Краткое резюме по фактам."}}]}}

    seen = {}

    def fake_post(url, headers, json, timeout):
        seen["url"] = url
        seen["headers"] = headers
        seen["json"] = json
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("sciknot.llm_summary.requests.post", fake_post)

    text, meta = generate_summary(bundle.question, bundle)

    assert text == "Краткое резюме по фактам."
    assert meta["status"] == "ok"
    assert meta["model"] == "yandexgpt-5.1"
    assert isinstance(meta["latency_ms"], int)
    assert seen["timeout"] == 12
    assert seen["json"]["completionOptions"]["temperature"] == 0.2
    assert seen["json"]["completionOptions"]["maxTokens"] == 300
    assert "fake-key" not in str(seen["json"])

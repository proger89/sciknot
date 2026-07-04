from __future__ import annotations

from pathlib import Path

from sciknot import literature_review
from sciknot.literature_review import (
    build_review_prompt,
    extract_keywords,
    extract_text,
    score_document,
    search_documents,
)


def test_extract_keywords_strips_stopwords():
    keywords = extract_keywords("Выполнить литературный обзор методов очистки шахтных вод")
    assert "шахтных" in keywords
    assert "очистки" in keywords
    # стоп-слова не попадают
    assert "литературный" not in keywords
    assert "обзор" not in keywords
    assert "выполнить" not in keywords


def test_extract_keywords_handles_technical_terms():
    keywords = extract_keywords("Циркуляция католита при электроэкстракции никеля")
    assert "католита" in keywords
    assert "электроэкстракции" in keywords
    assert "никеля" in keywords


def test_score_document_relevant_beats_irrelevant():
    keywords = extract_keywords("Удаление SO2 из отходящих газов")
    relevant_meta = {
        "path": "Источники информации/Обзоры/Удаление SO2 2018.docx",
        "topic_tags": "background",
    }
    irrelevant_meta = {
        "path": "Источники информации/Журналы/Горная промышленность №1.pdf",
        "topic_tags": "journal",
    }
    assert score_document(relevant_meta, "", keywords) > score_document(irrelevant_meta, "", keywords)
    assert score_document(relevant_meta, "", keywords) > 0


def test_score_document_text_match_counts():
    keywords = extract_keywords("циркуляция католита")
    meta = {"path": "doc.docx", "topic_tags": "background"}
    text_with = "В данной работе рассмотрена циркуляция католита при электроэкстракции."
    text_without = "Совершенно другая тема про обогащение руд."
    assert score_document(meta, text_with, keywords) > score_document(meta, text_without, keywords)


def test_search_documents_returns_sorted_top_k():
    question = "Удаление SO2 из отходящих газов металлургических предприятий"
    # передаём пустой кэш и ограничиваем — поиск не должен читать все PDF корпуса
    hits = search_documents(question, top_k=3, text_cache={})
    assert len(hits) <= 3
    assert len(hits) >= 1
    # отсортированы по убыванию score
    scores = [hit["score"] for hit in hits]
    assert scores == sorted(scores, reverse=True)
    # каждый hit имеет нужные поля
    for hit in hits:
        assert "document_id" in hit
        assert "score" in hit
        assert "path" in hit


def test_search_documents_empty_for_unknown_topic():
    hits = search_documents("квантовая запутанность фотонов в космосе", top_k=5)
    # тема не представлена в корпусе — должно быть пусто или почти пусто
    assert len(hits) <= 1


def test_extract_text_handles_missing_file():
    text = extract_text(Path("nonexistent_file_12345.pdf"))
    assert text == ""


def test_build_review_prompt_contains_question_and_sources():
    question = "Очистка шахтных вод"
    hits = [
        {"document_id": "SRC0001", "path": "doc1.docx", "text": "Шахтные воды очищаются реагентами."},
        {"document_id": "SRC0002", "path": "doc2.pdf", "text": "Мембранные методы очистки."},
    ]
    prompt = build_review_prompt(question, hits)
    assert "Очистка шахтных вод" in prompt
    assert "[SRC0001]" in prompt
    assert "[SRC0002]" in prompt
    assert "шахтные воды" in prompt.lower()


def test_generate_review_without_credentials_returns_none():
    import os

    old_key = os.environ.pop("YANDEX_API_KEY", None)
    old_folder = os.environ.pop("YANDEX_FOLDER_ID", None)
    try:
        review, meta = literature_review.generate_review("тест", [{"document_id": "X", "text": "y"}])
        assert review is None
        assert meta["status"] == "unavailable"
    finally:
        if old_key:
            os.environ["YANDEX_API_KEY"] = old_key
        if old_folder:
            os.environ["YANDEX_FOLDER_ID"] = old_folder

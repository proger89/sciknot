"""Литературный обзор по корпусу документов.

Отдельный режим, не зависящий от GraphRAG-демо: по вопросу находит релевантные
документы в корпусе (по ключевым словам), извлекает из них текст и генерирует
связный обзор через YandexGPT с цитированием источников.
"""

from __future__ import annotations

import csv
import os
import re
import time
from pathlib import Path
from typing import Any

import requests

from .paths import ROOT

YANDEX_COMPLETION_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
DEFAULT_MODEL_NAME = "yandexgpt-5.1"
MANIFEST_PATH = ROOT / "data" / "raw_manifest.csv"
MAX_TEXT_CHARS = 8000
DEFAULT_TOP_K = 6

# Стоп-слова русского языка, которые не несут смысловой нагрузки в техническом
# вопросе. Нормализуются (ё->е, lowercase) перед сравнением.
STOP_WORDS = frozenset(
    """
    и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по только ее мне было вот от меня
    еще нет о из ему теперь когда даже ну вдруг ли если или быть был него до вас нибудь опять уж вам ведь там
    потом себя ничего ей может они тут где есть надо ней для мы тебя их чем была сам чтобы без будто чего раз тоже
    себе под будет ж тогда кто этот того потому этого какой совсем ним здесь этом один почти мой тем чтобы нее
    сейчас были куда зачем всех никогда можно при наконец два об другой хоть после над больше тот через эти нас
    про всего них какая много разве три эту моя впрочем хорошо свою этой перед иногда лучше чуть том нельзя такой
    им более всегда конечно всю между
    выполнить литературный обзор методы метод способ способы области организации для Existing existing
    техники технических информации информации sources источников последние лет мировая отечественная
    мировой мира россии российской примеры примеров практики практики анализ современных современный
    производства горно металлургической цветной предприятий предприятия existing existing существующих
    """.split()
)

# Синонимы/расширения ключевых терминов, чтобы находить документы даже при
# разных формулировках вопроса. Ключ — токен из вопроса, значение — список
# вариантов для поиска в документе.
TERM_EXPANSIONS: dict[str, list[str]] = {
    "вод": ["вод", "сток", "очист", "обессол", "опресн", "фильтр"],
    "шахтн": ["шахт", "рудничн"],
    "католит": ["католит", "катодн"],
    "электроэкстракц": ["электроэкстракц", "электролиз", "электролитн", "ew"],
    "электролит": ["электролит", "электролиз", "ванны", "ванн"],
    "диафрагм": ["диафрагм", "ячее"],
    "гипс": ["гипс", "ангидрит"],
    "so2": ["so2", "so 2", "серн", "серы", "сера", "сульф"],
    "уголь": ["уголь", "coal", "золь"],
    "закладк": ["закладк", "закладочн", "выработанн"],
    "штейн": ["штейн", "штейн"],
    "шлак": ["шлак", "шлак"],
    "медн": ["медн", "медь", "cu "],
    "никел": ["никел", "ni "],
    "кобальт": ["кобальт", "co "],
    "свинец": ["свинец", "свинц", "pb "],
    "цинк": ["цинк", "zn "],
    "мпг": ["мпг", "платин", "паллади", "роди", "благородн"],
    "обогатительн": ["обогат", "фабрик", "флотаци"],
    "сульфат": ["сульфат"],
    "хлорид": ["хлорид"],
}


def normalize(text: str) -> str:
    return text.casefold().replace("ё", "е").strip()


def extract_keywords(question: str) -> list[str]:
    """Извлечь значимые термины из вопроса (без стоп-слов)."""
    normalized = normalize(question)
    tokens = re.findall(r"[a-zа-я0-9]+", normalized)
    keywords = [token for token in tokens if len(token) >= 3 and token not in STOP_WORDS]
    # сохраняем порядок и уникальность
    seen: set[str] = set()
    result: list[str] = []
    for token in keywords:
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result


def expand_keywords(keywords: list[str]) -> list[str]:
    """Расширить ключевые слова синонимами для более широкого поиска."""
    expanded: list[str] = list(keywords)
    for keyword in keywords:
        for prefix, variants in TERM_EXPANSIONS.items():
            if keyword.startswith(prefix) or prefix.startswith(keyword):
                for variant in variants:
                    if variant not in expanded:
                        expanded.append(variant)
    return expanded


def _read_manifest() -> list[dict[str, str]]:
    if not MANIFEST_PATH.exists():
        return []
    with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def extract_text(path: Path) -> str:
    """Извлечь текст из PDF/DOCX. При сбое — пустая строка."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _extract_pdf(path)
        if suffix in {".docx", ".doc"}:
            return _extract_docx(path)
    except Exception:
        return ""
    return ""


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text:
            parts.append(text)
        if sum(len(part) for part in parts) >= MAX_TEXT_CHARS:
            break
    return "\n".join(parts)[:MAX_TEXT_CHARS]


def _extract_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError:
        return ""
    document = Document(str(path))
    parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
    return "\n".join(parts)[:MAX_TEXT_CHARS]


def score_document(meta: dict[str, str], text: str, keywords: list[str]) -> int:
    """Оценить релевантность документа по ключевым словам."""
    if not keywords:
        return 0
    path_norm = normalize(meta.get("path", ""))
    title_norm = normalize(Path(meta.get("path", "")).name)
    tags_norm = normalize(meta.get("topic_tags", ""))
    text_norm = normalize(text) if text else ""
    expanded = expand_keywords(keywords)
    score = 0
    matched: set[str] = set()
    for keyword in expanded:
        if keyword in matched:
            continue
        if keyword in title_norm:
            score += 3
            matched.add(keyword)
        elif keyword in path_norm:
            score += 2
            matched.add(keyword)
        elif keyword in tags_norm:
            score += 2
            matched.add(keyword)
        elif keyword in text_norm:
            score += 1
            matched.add(keyword)
    return score


def search_documents(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    text_cache: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Найти top_k релевантных документов. Возвращает список с метаданными и текстом.

    Двухфазный поиск: сначала скорим все документы по метаданным (быстро), затем
    извлечём текст только для топ-N кандидатов (медленно) и пересчитаем счёт.
    """
    keywords = extract_keywords(question)
    if not keywords:
        return []
    manifest = _read_manifest()
    if text_cache is None:
        text_cache = {}

    # Фаза 1: скоринг по метаданным (path, title, tags) — без чтения файлов.
    meta_scored: list[dict[str, Any]] = []
    for meta in manifest:
        score = score_document(meta, "", keywords)
        if score > 0:
            meta_scored.append({**meta, "score": score, "text": ""})
    meta_scored.sort(key=lambda item: item["score"], reverse=True)

    # Фаза 2: для топ-N кандидатов извлекаем текст и пересчитываем счёт.
    candidates = meta_scored[: top_k * 3]
    for item in candidates:
        doc_id = item.get("document_id", "")
        file_path = ROOT / item.get("path", "")
        text = text_cache.get(doc_id, "")
        if not text and file_path.exists() and file_path.suffix.lower() in {".pdf", ".docx"}:
            text = extract_text(file_path)
            text_cache[doc_id] = text
        item["text"] = text
        item["score"] = score_document(item, text, keywords)

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return [item for item in candidates[:top_k] if item["score"] > 0]


def build_review_prompt(question: str, hits: list[dict[str, Any]]) -> str:
    """Построить промпт для генерации литобзора."""
    context_parts: list[str] = []
    for hit in hits:
        doc_id = hit.get("document_id", "")
        title = Path(hit.get("path", "")).name
        text = hit.get("text", "")
        snippet = text[:3000] if text else "(текст документа недоступен)"
        context_parts.append(f"[{doc_id}] {title}\n{snippet}")
    context = "\n\n---\n\n".join(context_parts)
    instructions = (
        "Ты — помощник инженера-исследователя горно-металлургической компании. "
        "На основе приведённых отрывков из корпоративного корпуса документов составь "
        "связный литературный обзор по вопросу пользователя.\n\n"
        "Правила:\n"
        "1. Опирайся ТОЛЬКО на приведённые отрывки. Не выдумывай факты, цифры и методы.\n"
        "2. Цитируй источники в формате [SRC0001] сразу после утверждения.\n"
        "3. Группируй информацию по темам/подходам, а не по документам.\n"
        "4. Если в отрывках мало данных по вопросу — честно скажи об этом и укажи, "
        "каких именно данных не хватает.\n"
        "5. Объём — 3-5 абзацев. Отвечай по-русски."
    )
    return f"{instructions}\n\nВопрос: {question}\n\nОтрывки из документов:\n\n{context}"


def llm_available() -> bool:
    return bool(os.environ.get("YANDEX_API_KEY") and os.environ.get("YANDEX_FOLDER_ID"))


def generate_review(question: str, hits: list[dict[str, Any]]) -> tuple[str | None, dict[str, Any]]:
    """Сгенерировать литобзор через YandexGPT. Возвращает (текст|None, meta)."""
    api_key = os.environ.get("YANDEX_API_KEY")
    folder_id = os.environ.get("YANDEX_FOLDER_ID")
    if not api_key or not folder_id or not hits:
        return None, {"status": "unavailable", "detail": "credentials_absent" if not hits else "no_documents"}

    model_uri = f"gpt://{folder_id}/{DEFAULT_MODEL_NAME}"
    prompt = build_review_prompt(question, hits)
    started = time.perf_counter()
    try:
        response = requests.post(
            YANDEX_COMPLETION_URL,
            headers={"Authorization": f"Api-Key {api_key}", "Content-Type": "application/json"},
            json={
                "modelUri": model_uri,
                "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": "8000"},
                "messages": [{"role": "user", "text": prompt}],
            },
            timeout=45,
        )
    except requests.RequestException as exc:
        return None, {"status": "unavailable", "detail": exc.__class__.__name__}

    latency_ms = round((time.perf_counter() - started) * 1000)
    if not response.ok:
        return None, {"status": "unavailable", "detail": f"http_status={response.status_code}"}

    try:
        payload = response.json()
        text = payload["result"]["alternatives"][0]["message"]["text"].strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return None, {"status": "unavailable", "detail": exc.__class__.__name__}

    if not text:
        return None, {"status": "unavailable", "detail": "empty_response"}
    return text, {"status": "ok", "model": DEFAULT_MODEL_NAME, "latency_ms": latency_ms}

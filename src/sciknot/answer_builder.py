from __future__ import annotations

from statistics import mean
from typing import Any

from .contradictions import find_contradictions
from .evidence_store import claims_for_rows
from .gap_analysis import detect_gaps
from .models import AnswerBundle
from .subgraph import build_subgraph


def fact_phrase(count: int) -> str:
    last_two = count % 100
    last = count % 10
    if last == 1 and last_two != 11:
        return f"найден {count} подтвержденный факт"
    if 2 <= last <= 4 and not 12 <= last_two <= 14:
        return f"найдено {count} подтвержденных факта"
    return f"найдено {count} подтвержденных фактов"


def gap_phrase(count: int) -> str:
    last_two = count % 100
    last = count % 10
    if last == 1 and last_two != 11:
        return f"найден {count} пробел"
    if 2 <= last <= 4 and not 12 <= last_two <= 14:
        return f"найдено {count} пробела"
    return f"найдено {count} пробелов"


def subject_label(question: str, intent: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    if intent.get("type") in {"gap", "insufficient"}:
        return "по данным НДС и прогнозу концентрации напряжений"

    joined = " ".join(
        [
            question,
            *[str(row["process"]) for row in rows],
            *[str(row["property_name"]) for row in rows],
        ]
    ).lower()
    if "ндс" in joined:
        material = intent.get("material") or rows[0]["material"]
        if material == "Комсомольский рудный массив":
            return "напряженно-деформированному состоянию (НДС) Комсомольского рудного массива"
        return f"напряженно-деформированному состоянию (НДС): {material}"
    return "выбранной теме"


def signal_text(row: dict[str, Any]) -> str:
    if row["process"] == "измерение НДС" and row["property_name"] == "уровень напряжений":
        return f"выполнялись измерения уровня напряжений (источник {row['source_document_id']})"
    return f"{row['process']}: {row['property_name']} (источник {row['source_document_id']})"


def build_answer(question: str, intent: dict[str, Any], rows: list[dict[str, Any]]) -> AnswerBundle:
    if not rows:
        missing = ["Нет строк таблицы для выбранного объекта/свойства."]
        return AnswerBundle(
            question=question,
            intent=intent,
            summary="Недостаточно данных: граф не нашел релевантных экспериментов в curated slice.",
            experiment_rows=[],
            evidence=[],
            gaps=[],
            contradictions=[],
            confidence=0.1,
            data_insufficient=True,
            missing_data=missing,
            subgraph={"nodes": [], "edges": []},
        )

    claims = claims_for_rows(rows)
    gaps = detect_gaps(rows)
    contradictions = find_contradictions(rows)
    confidence = round(mean(float(row["confidence"]) for row in rows), 2)
    missing = [gap.reason for gap in gaps]
    source_ids = sorted({row["source_document_id"] for row in rows})
    signals = "; ".join(signal_text(row) for row in rows[:3])
    if intent.get("type") in {"gap", "insufficient"}:
        summary = f"В демо-срезе {subject_label(question, intent, rows)} {gap_phrase(len(rows))}: {signals}."
    else:
        summary = f"По {subject_label(question, intent, rows)} {fact_phrase(len(rows))}: {signals}."
    if len(source_ids) < 3:
        if len(source_ids) == 1:
            summary += " Вывод основан на единственном источнике — для надежной картины данных недостаточно."
        else:
            summary += " Источников меньше трех — вывод требует дополнительного независимого подтверждения."
    if any(gap.severity == "high" for gap in gaps):
        summary += " Есть критические пробелы: нужны прямые замеры или верификация прогноза."

    return AnswerBundle(
        question=question,
        intent=intent,
        summary=summary,
        experiment_rows=rows,
        evidence=claims,
        gaps=gaps,
        contradictions=contradictions,
        confidence=confidence,
        data_insufficient=bool(gaps),
        missing_data=missing,
        subgraph=build_subgraph(rows),
    )

from __future__ import annotations

from typing import Any

from .answer_builder import build_answer
from .graph_queries import fetch_all, fetch_experiments, require_db
from .models import AnswerBundle
from .paths import PROCESSED
from .query_parser import known_entities, parse_question


def retrieve_answer(question: str, db_path=None) -> tuple[AnswerBundle | None, dict[str, Any]]:
    target = db_path or PROCESSED / "sciknot.sqlite"
    require_db(target)
    intent = parse_question(question)
    trace: dict[str, Any] = {
        "intent": intent,
        "recognized": bool(intent.get("recognized")),
        "entities": intent.get("entities", []),
        "known_entities": known_entities(),
        "query_strategy": "exact",
    }
    if not trace["recognized"]:
        trace.update({"facts_count": 0, "sources_count": 0, "data_insufficient": True})
        return None, trace

    rows = fetch_experiments(
        material=intent.get("material"),
        process=intent.get("process"),
        property_name=intent.get("property_name"),
        path=target,
    )
    if not rows:
        rows = fetch_experiments(material=intent.get("material"), path=target)
        trace["query_strategy"] = "material_fallback"
    if intent["type"] in {"gap", "insufficient"}:
        all_rows = fetch_all(target)
        gap_rows = [row for row in all_rows if row["value"] == "missing" or row["trend"] == "unknown"]
        rows = gap_rows or rows
        trace["query_strategy"] = "gap_rows"
    bundle = build_answer(question, intent, rows)
    trace.update(
        {
            "facts_count": len(rows),
            "sources_count": len({row["source_document_id"] for row in rows}),
            "data_insufficient": bundle.data_insufficient,
        }
    )
    return bundle, trace


def answer_question(question: str, db_path=None) -> AnswerBundle:
    bundle, trace = retrieve_answer(question, db_path)
    if bundle is not None:
        return bundle
    return build_answer(question, trace["intent"], [])

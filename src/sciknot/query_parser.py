from __future__ import annotations

from .catalog import load_dictionary
from .linking import find_mentions


def known_entities() -> list[str]:
    return list(load_dictionary("materials"))


def parse_question(question: str) -> dict[str, str | None]:
    materials = find_mentions(question, load_dictionary("materials"))
    if "Комсомольский рудный массив" in materials and "горный массив" in materials:
        materials = [item for item in materials if item != "горный массив"]
    processes = find_mentions(question, load_dictionary("regimes"))
    properties = find_mentions(question, load_dictionary("properties"))
    normalized = question.casefold()
    if not processes and "прогноз" in normalized and "напряж" in normalized:
        processes = ["прогноз концентраций"]
    if not properties and "концентрац" in normalized and "напряж" in normalized:
        properties = ["вероятность концентрации напряжений"]
    entities = [*materials, *processes, *properties]

    intent_type = "main"
    if any(word in normalized for word in ("пробел", "не хватает", "нет данных", "gap")):
        intent_type = "gap"
    if any(word in normalized for word in ("недостаточно", "достаточно ли", "нет замеров", "insufficient")):
        intent_type = "insufficient"

    return {
        "type": intent_type,
        "material": materials[0] if materials else "Комсомольский рудный массив",
        "process": processes[0] if processes else None,
        "property_name": properties[0] if properties else None,
        "entities": entities,
        "recognized": bool(entities),
    }

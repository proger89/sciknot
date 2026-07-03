from __future__ import annotations

from difflib import SequenceMatcher


def normalize(value: str) -> str:
    return " ".join(value.casefold().replace("ё", "е").split())


def link_entity(query: str, dictionary: dict[str, list[str]], threshold: float = 0.72) -> tuple[str | None, float]:
    needle = normalize(query)
    if not needle:
        return None, 0.0

    best: tuple[str | None, float] = (None, 0.0)
    for canonical, aliases in dictionary.items():
        for alias in aliases:
            norm_alias = normalize(alias)
            if needle == norm_alias or norm_alias in needle or needle in norm_alias:
                return canonical, 1.0
            score = SequenceMatcher(None, needle, norm_alias).ratio()
            if score > best[1]:
                best = (canonical, score)

    if best[1] >= threshold:
        return best
    return None, best[1]


def find_mentions(text: str, dictionary: dict[str, list[str]]) -> list[str]:
    haystack = normalize(text)
    scored: list[tuple[int, str]] = []
    for canonical, aliases in dictionary.items():
        matches = [normalize(alias) for alias in aliases if normalize(alias) in haystack]
        if matches:
            scored.append((max(len(match) for match in matches), canonical))
    scored.sort(reverse=True)
    return [canonical for _, canonical in scored]

from sciknot.contradictions import find_contradictions
from sciknot.graph_queries import fetch_all


def test_contradictions_returns_explicit_status():
    result = find_contradictions(fetch_all())
    assert result
    assert result[0].status in {"source_backed", "none_found"}


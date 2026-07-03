from sciknot.gap_analysis import detect_gaps
from sciknot.graph_queries import fetch_all


def test_gap_analysis_finds_missing_measurements():
    gaps = detect_gaps(fetch_all())
    assert any(gap.gap_type == "missing_measurement" for gap in gaps)


def test_gap_analysis_flags_single_source_evidence():
    row = fetch_all()[0]
    gaps = detect_gaps([row])
    assert any(gap.gap_type == "weak_evidence" for gap in gaps)

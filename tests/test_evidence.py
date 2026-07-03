from sciknot.evidence_store import claim_from_row
from sciknot.graph_queries import fetch_all


def test_claim_from_row_has_source_ref():
    row = fetch_all()[0]
    claim = claim_from_row(row)
    assert claim.source.document_id == row["source_document_id"]
    assert claim.source.quote


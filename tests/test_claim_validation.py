from sciknot.models import EvidenceClaim, SourceRef


def test_evidence_claim_accepts_valid_source():
    claim = EvidenceClaim(
        claim_id="CLM",
        entity="Комсомольский рудный массив",
        property_name="уровень напряжений",
        value="high",
        source=SourceRef(document_id="DOC001", locator="title", quote="НДС Комсомольский"),
        confidence=0.8,
    )
    assert claim.status == "accepted"


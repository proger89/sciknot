import pytest
from pydantic import ValidationError

from sciknot.models import SourceRef


def test_source_ref_requires_quote():
    with pytest.raises(ValidationError):
        SourceRef(document_id="DOC", locator="p.1", quote="")


def test_source_ref_accepts_quote():
    ref = SourceRef(document_id="DOC", locator="title", quote="НДС Комсомольский")
    assert ref.quote == "НДС Комсомольский"


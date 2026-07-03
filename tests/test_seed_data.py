from sciknot.catalog import load_documents, load_experiments


def test_seed_data_has_demo_scale():
    assert len(load_documents()) >= 5
    records = load_experiments()
    assert len(records) >= 12
    assert all(record.source.document_id for record in records)
    assert all(record.source.quote for record in records)


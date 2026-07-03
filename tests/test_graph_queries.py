from sciknot.graph_queries import fetch_experiments


def test_fetch_demo_rows_after_build():
    rows = fetch_experiments(material="Комсомольский рудный массив")
    assert rows
    assert any(row["source_document_id"] == "DOC001" for row in rows)


# Architecture

SciKnot Navigator uses a table-first GraphRAG path:

1. Full raw corpus manifest plus curated demo source slice and experiment table.
2. Pydantic schemas for facts, sources, evidence claims, gaps, and answer bundles.
3. SQLite stores normalized experiment rows.
4. A bounded graph snapshot connects experiments, materials, processes, properties, and documents.
5. Retrieval parses Russian questions, filters the table graph, attaches evidence claims, and reports gaps.
6. Streamlit renders the answer table, source quotes, gap list, and bounded subgraph.

The MVP inventories the full corpus into `data/raw_manifest.csv`, but intentionally does not parse every PDF into graph facts. PDF/DOCX/PPTX documents are an evidence layer for a curated 5-10 document slice.

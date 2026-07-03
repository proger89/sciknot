.PHONY: install test lint smoke graph demo

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

lint:
	python -m ruff check .

smoke:
	python scripts/smoke_demo.py

graph:
	python scripts/build_graph.py --seed data/curated/experiments_seed.csv --out data/processed/sciknot.sqlite
	python scripts/export_graph_snapshot.py --db data/processed/sciknot.sqlite --out data/processed/graph_snapshot.json

demo:
	streamlit run app.py --server.port 8501


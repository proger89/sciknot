#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
fi

if docker compose config >/dev/null 2>&1; then
  docker compose up --build -d
else
  python -m pip install -r requirements.txt
  python scripts/prepare_demo_data.py
  python -m streamlit run app.py --server.port 8501 &
fi

echo "Demo URL: http://localhost:8501"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:8501 >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open http://localhost:8501 >/dev/null 2>&1 || true
fi

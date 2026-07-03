# SciKnot Navigator

Table-first GraphRAG MVP для задачи "Научный клубок": полный manifest корпуса `Источники информации/`, небольшой curated-граф для демо, ответы на русские вопросы, источники, пробелы и ограниченный 2-hop подграф.

## Быстрый запуск через Docker

```powershell
copy .env.example .env
.\scripts\start_demo.ps1
```

Скрипт сам соберет Docker-образ, запустит сервис и откроет `http://localhost:8501` в браузере. Если Docker недоступен, скрипт перейдет на локальный Streamlit fallback.

Что заполнять в `.env`:

```dotenv
YANDEX_API_KEY=
YANDEX_FOLDER_ID=
```

Без этих значений UI работает в deterministic GraphRAG-режиме. С ними появится переключатель `LLM-резюме (YandexGPT)`.

Подготовка данных выполняется автоматически при запуске:

- `data/raw_manifest.csv` - manifest файлов из `Источники информации/`.
- `data/processed/sciknot.sqlite` - SQLite-граф по curated таблице.
- `data/processed/graph_snapshot.json` - snapshot графа для UI.

Ручной Docker fallback:

```powershell
docker compose up --build
```

Локальный fallback без Docker:

```powershell
python -m pip install -r requirements.txt
python scripts/prepare_demo_data.py
python -m streamlit run app.py --server.port 8501
```

После ручного запуска откройте `http://localhost:8501`.

## Что внутри

- `data/raw_manifest.csv` - manifest всего найденного корпуса.
- `data/curated/experiments_seed.csv` - 12 вручную курированных строк по геомеханике и НДС.
- `src/sciknot/` - схемы, linking, graph store, retrieval, gap analysis.
- `scripts/` - подготовка данных, сборка графа, smoke-проверки, Yandex sanity probe и launch fallback.
- `docs/RUN_RU.md` - инструкция для жюри.

Yandex AI Studio ключи читаются только из `.env` или окружения: `YANDEX_API_KEY`, `YANDEX_FOLDER_ID`.

## UI

В `Демо-вопрос` radio выбирает сценарий, pills выбирают один из 12 проверенных вопросов, а кнопка `Найти ответ` всегда отвечает на текущий текст поля.

# README для жюри

## 1. Запуск через Docker

```powershell
copy .env.example .env
.\scripts\start_demo.ps1
```

URL: `http://localhost:8501` откроется в браузере автоматически. Если запускаете вручную, используйте `docker compose up --build` и откройте URL сами.

## 2. Fallback без Docker

```powershell
python -m pip install -r requirements.txt
python scripts/prepare_demo_data.py
streamlit run app.py --server.port 8501
```

## 3. Где добавить Yandex key

В файле `.env`, только локально:

```dotenv
YANDEX_API_KEY=
YANDEX_FOLDER_ID=
```

Без ключа демо работает в deterministic GraphRAG/table-first режиме. С ключом в сайдбаре появляется переключатель `LLM-резюме (YandexGPT)`: поиск фактов остаётся детерминированным, а модель только формулирует краткое резюме по найденным фактам.

Текущий sanity-probe выбрал `yandexgpt-5.1`: default-модель отвечает HTTP 200. Fallback `qwen3-235b-a22b-fp8` оставлен в конфиге, но текущий API probe вернул HTTP 400.

## 4. Что именно индексируется

Демо честно разделяет два слоя:

- `data/raw_manifest.csv` - manifest всего корпуса файлов, чтобы показать покрытие входных данных.
- `data/curated/experiments_seed.csv` и SQLite graph - curated slice для надежного demo answer path.

Полный semantic parsing всех PDF не заявляется как выполненный в дедлайн-версии.

## 5. Демо-вопросы

В UI подготовлено 12 проверенных вопросов: 5 для `Главный ответ`, 4 для `Пробелы`, 3 для `Недостаточно данных`. Radio выбирает категорию, pills выбирают вариант, а кнопка `Найти ответ` всегда запускает поиск по текущему тексту поля.

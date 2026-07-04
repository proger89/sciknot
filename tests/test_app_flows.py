from streamlit.testing.v1 import AppTest

from sciknot.demo_questions import PREPARED_QUESTIONS


def run_app() -> AppTest:
    """Запустить приложение в режиме GraphRAG-демо (дефолт)."""
    app = AppTest.from_file("app.py", default_timeout=10)
    app.session_state["app_mode"] = "GraphRAG-демо"
    return app.run()


def gradio(app: AppTest) -> AppTest:
    """Radio выбора демо-вопроса (radio[0] — режим, radio[1] — демо-вопрос)."""
    return app.radio[1]


def subheaders(app: AppTest) -> list[str]:
    return [item.value for item in app.subheader]


def warnings(app: AppTest) -> list[str]:
    return [item.value for item in app.warning]


def test_initial_state_has_no_answer_sections():
    app = run_app()

    assert app.text_input[0].value == ""
    assert app.button[0].label == "Найти ответ"
    assert "Ответ" not in subheaders(app)
    assert any(item.value == "Выберите пример выше или задайте свой вопрос." for item in app.info)


def test_radio_fills_question_without_rendering_answer():
    app = run_app()
    gradio(app).set_value("Главный ответ").run(timeout=10)

    assert app.text_input[0].value == PREPARED_QUESTIONS["Главный ответ"][0].question
    assert "Ответ" not in subheaders(app)


def test_search_renders_answer_sections():
    app = run_app()
    gradio(app).set_value("Главный ответ").run(timeout=10)
    app.button[0].click().run(timeout=15)

    assert subheaders(app) == ["Ответ", "Таблица фактов", "Источники и цитаты", "Пробелы", "Противоречия", "Карта связей ответа"]
    assert len(app.dataframe) == 1
    assert any("Поиск занял" in item.value and "1 факт" in item.value for item in app.caption)


def test_pill_fills_variant_without_rendering_answer():
    app = run_app()
    gradio(app).set_value("Главный ответ").run(timeout=10)

    assert len(app.pills) == 1
    app.pills[0].set_value("Плотность наблюдений").run(timeout=10)

    assert app.text_input[0].value == PREPARED_QUESTIONS["Главный ответ"][1].question
    assert "Ответ" not in subheaders(app)


def test_switching_category_resets_prior_pill():
    app = run_app()
    gradio(app).set_value("Главный ответ").run(timeout=10)
    app.pills[0].set_value("Плотность наблюдений").run(timeout=10)
    gradio(app).set_value("Пробелы").run(timeout=10)

    assert app.text_input[0].value == PREPARED_QUESTIONS["Пробелы"][0].question
    assert app.pills[0].value is None
    assert "Ответ" not in subheaders(app)


def test_blank_submit_preserves_previous_answer():
    app = run_app()
    gradio(app).set_value("Главный ответ").run(timeout=10)
    app.button[0].click().run(timeout=15)
    app.text_input[0].set_value("").run(timeout=10)
    app.button[0].click().run(timeout=10)

    assert "Введите вопрос или выберите пример выше." in warnings(app)
    assert "Ответ" in subheaders(app)


def test_unknown_fallback_entity_button_fills_question_without_exception():
    app = run_app()
    app.text_input[0].set_value("Что известно про климатические выбросы?").run(timeout=10)
    app.button[0].click().run(timeout=15)

    assert "Не удалось сопоставить вопрос с известными сущностями графа." in warnings(app)
    assert any(button.label == "Комсомольский рудный массив" for button in app.button)

    app.button[1].click().run(timeout=10)

    assert len(app.exception) == 0
    assert app.text_input[0].value == "Что известно про Комсомольский рудный массив?"


def test_llm_toggle_hidden_without_credentials(monkeypatch):
    monkeypatch.delenv("YANDEX_API_KEY", raising=False)
    monkeypatch.delenv("YANDEX_FOLDER_ID", raising=False)
    monkeypatch.setattr("sciknot.llm_summary.load_env_file", lambda *args, **kwargs: None)

    app = run_app()

    assert len(app.toggle) == 0


def _old_test_llm_toggle_renders_mocked_summary(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "fake-key")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "fake-folder")

    def fake_generate_summary(question, bundle):
        return "LLM summary strictly from facts.", {
            "status": "ok",
            "model": "yandexgpt-5.1",
            "latency_ms": 12,
        }

    monkeypatch.setattr("sciknot.llm_summary.generate_summary", fake_generate_summary)

    app = run_app()
    assert app.toggle[0].label == "LLM-резюме (YandexGPT)"
    app.toggle[0].set_value(True).run(timeout=10)
    gradio(app).set_value("Р“Р»Р°РІРЅС‹Р№ РѕС‚РІРµС‚").run(timeout=10)
    app.button[0].click().run(timeout=15)

    assert "LLM-резюме" in subheaders(app)
    assert any(item.value == "LLM summary strictly from facts." for item in app.success)
    assert "РћС‚РІРµС‚" in subheaders(app)


def _old_test_llm_failure_keeps_deterministic_answer(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "fake-key")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "fake-folder")

    def fake_generate_summary(question, bundle):
        return None, {"status": "unavailable", "detail": "Timeout"}

    monkeypatch.setattr("sciknot.llm_summary.generate_summary", fake_generate_summary)

    app = run_app()
    app.toggle[0].set_value(True).run(timeout=10)
    gradio(app).set_value("Р“Р»Р°РІРЅС‹Р№ РѕС‚РІРµС‚").run(timeout=10)
    app.button[0].click().run(timeout=15)

    assert "LLM-резюме" not in subheaders(app)
    assert "РћС‚РІРµС‚" in subheaders(app)
    assert len(app.exception) == 0


def test_llm_toggle_renders_mocked_summary(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "fake-key")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "fake-folder")

    def fake_generate_summary(question, bundle):
        return "LLM summary strictly from facts.", {
            "status": "ok",
            "model": "yandexgpt-5.1",
            "latency_ms": 12,
        }

    monkeypatch.setattr("sciknot.llm_summary.generate_summary", fake_generate_summary)

    app = run_app()
    assert app.toggle[0].label.startswith("LLM-")
    app.toggle[0].set_value(True).run(timeout=10)
    gradio(app).set_value(gradio(app).options[0]).run(timeout=10)
    app.button[0].click().run(timeout=15)

    assert any("LLM" in value for value in subheaders(app))
    assert any(item.value == "LLM summary strictly from facts." for item in app.success)
    assert len(app.dataframe) == 1


def test_llm_failure_keeps_deterministic_answer(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "fake-key")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "fake-folder")

    def fake_generate_summary(question, bundle):
        return None, {"status": "unavailable", "detail": "Timeout"}

    monkeypatch.setattr("sciknot.llm_summary.generate_summary", fake_generate_summary)

    app = run_app()
    app.toggle[0].set_value(True).run(timeout=10)
    gradio(app).set_value(gradio(app).options[0]).run(timeout=10)
    app.button[0].click().run(timeout=15)

    assert not any("LLM" in value for value in subheaders(app))
    assert len(app.dataframe) == 1
    assert len(app.exception) == 0

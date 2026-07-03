import pytest

from sciknot.catalog import load_dictionary
from sciknot.demo_questions import PREPARED_QUESTIONS, all_demo_questions
from sciknot.retrieval import retrieve_answer

EXPECTED_COUNTS = {
    "Главный ответ": 5,
    "Пробелы": 4,
    "Недостаточно данных": 3,
}


def flatten_aliases(dictionary_name: str) -> set[str]:
    return {
        alias.casefold()
        for aliases in load_dictionary(dictionary_name).values()
        for alias in aliases
    }


def test_demo_question_catalog_counts_and_uniqueness():
    assert {category: len(questions) for category, questions in PREPARED_QUESTIONS.items()} == EXPECTED_COUNTS

    labels = [question.label for _, question in all_demo_questions()]
    full_questions = [question.question for _, question in all_demo_questions()]

    assert all(label.strip() for label in labels)
    assert all(question.strip() for question in full_questions)
    assert len(full_questions) == 12
    assert len(full_questions) == len(set(full_questions))


def test_requested_stem_aliases_exist_in_curated_dictionaries():
    aliases = {
        "materials": flatten_aliases("materials"),
        "regimes": flatten_aliases("regimes"),
        "properties": flatten_aliases("properties"),
    }

    assert "комсомольск" in aliases["materials"]
    assert "блочн" in aliases["regimes"]
    assert "деформац" in aliases["properties"]
    assert "замер" in aliases["properties"]
    assert "мониторинг" in aliases["properties"]
    assert "концентрации напряжений" in aliases["properties"]
    assert "валидац" in aliases["properties"]


@pytest.mark.parametrize(("category", "demo_question"), all_demo_questions())
def test_every_demo_question_resolves_to_graph_answer(category, demo_question):
    bundle, trace = retrieve_answer(demo_question.question)

    assert category in EXPECTED_COUNTS
    assert trace["recognized"] is True
    assert bundle is not None
    assert trace["facts_count"] > 0

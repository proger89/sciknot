from sciknot.answer_builder import fact_phrase
from sciknot.retrieval import answer_question, retrieve_answer


def test_main_answer_bundle():
    bundle = answer_question("Что известно про НДС Комсомольский?")
    assert bundle.experiment_rows
    assert bundle.subgraph["nodes"]
    assert bundle.confidence > 0
    assert bundle.data_insufficient
    assert "единственном источнике" in bundle.summary


def test_gap_answer_bundle():
    bundle = answer_question("Какие пробелы есть по рудоспускам?")
    assert bundle.gaps


def test_retrieve_answer_traces_unknown_question():
    bundle, trace = retrieve_answer("Что известно про климатические выбросы?")
    assert bundle is None
    assert not trace["recognized"]
    assert trace["facts_count"] == 0
    assert "Комсомольский рудный массив" in trace["known_entities"]


def test_fact_phrase_russian_pluralization():
    assert fact_phrase(1) == "найден 1 подтвержденный факт"
    assert fact_phrase(2) == "найдено 2 подтвержденных факта"
    assert fact_phrase(5) == "найдено 5 подтвержденных фактов"

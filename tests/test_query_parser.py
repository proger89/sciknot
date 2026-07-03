from sciknot.query_parser import parse_question


def test_parse_main_question():
    intent = parse_question("Что известно про НДС Комсомольский?")
    assert intent["material"] == "Комсомольский рудный массив"
    assert intent["recognized"]
    assert "Комсомольский рудный массив" in intent["entities"]


def test_parse_gap_question():
    intent = parse_question("Какие пробелы есть по рудоспускам?")
    assert intent["type"] == "gap"


def test_parse_unknown_question_marks_unrecognized():
    intent = parse_question("Что известно про климатические выбросы?")
    assert intent["material"] == "Комсомольский рудный массив"
    assert not intent["recognized"]


def test_parse_insufficient_question_recognizes_prediction_terms():
    intent = parse_question("Достаточно ли данных, чтобы подтвердить прогноз концентрации напряжений?")
    assert intent["type"] == "insufficient"
    assert intent["recognized"]
    assert intent["process"] == "прогноз концентраций"

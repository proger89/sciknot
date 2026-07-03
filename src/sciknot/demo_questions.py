from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoQuestion:
    label: str
    question: str


PREPARED_QUESTIONS: dict[str, list[DemoQuestion]] = {
    "Главный ответ": [
        DemoQuestion(
            "НДС и источники",
            "Что известно про напряженно-деформированное состояние (НДС) Комсомольского рудного массива и какие источники это подтверждают?",
        ),
        DemoQuestion(
            "Плотность наблюдений",
            "Какая плотность наблюдений за НДС на Комсомольском рудном массиве?",
        ),
        DemoQuestion(
            "Блочная модель",
            "Что показало блочное моделирование Комсомольского рудного массива?",
        ),
        DemoQuestion(
            "Риск рудоспусков",
            "Что известно про риск деформаций рудоспусков?",
        ),
        DemoQuestion(
            "Мониторинг 2025",
            "Какой приоритет у мониторинга геомеханических рисков в плане Рудник 2025?",
        ),
    ],
    "Пробелы": [
        DemoQuestion(
            "Рудоспуски и замеры",
            "Какие пробелы есть по рудоспускам и фактическим замерам напряженно-деформированного состояния (НДС)?",
        ),
        DemoQuestion(
            "Верификация прогноза",
            "Какие пробелы есть в верификации прогноза концентрации напряжений?",
        ),
        DemoQuestion(
            "Мониторинг массива",
            "Каких данных не хватает по мониторингу горного массива?",
        ),
        DemoQuestion(
            "Замеры НДС",
            "Где не хватает фактических замеров НДС?",
        ),
    ],
    "Недостаточно данных": [
        DemoQuestion(
            "Прогноз концентраций",
            "Достаточно ли данных, чтобы подтвердить прогноз концентрации напряжений?",
        ),
        DemoQuestion(
            "Замеры рудоспусков",
            "Достаточно ли фактических замеров НДС по рудоспускам?",
        ),
        DemoQuestion(
            "Валидация модели",
            "Достаточно ли данных для валидации блочной модели?",
        ),
    ],
}


def all_demo_questions() -> list[tuple[str, DemoQuestion]]:
    return [
        (category, question)
        for category, questions in PREPARED_QUESTIONS.items()
        for question in questions
    ]


def first_question(category: str) -> DemoQuestion:
    return PREPARED_QUESTIONS[category][0]


def question_labels(category: str) -> list[str]:
    return [question.label for question in PREPARED_QUESTIONS[category]]


def question_by_label(category: str, label: str) -> DemoQuestion:
    for question in PREPARED_QUESTIONS[category]:
        if question.label == label:
            return question
    raise KeyError(f"Unknown demo question label: {category}/{label}")

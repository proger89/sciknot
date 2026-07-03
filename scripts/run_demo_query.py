from __future__ import annotations

import argparse
import json
from pathlib import Path

from sciknot.retrieval import answer_question

QUESTIONS = {
    "main": "Что известно про напряженно-деформированное состояние (НДС) Комсомольского рудного массива и какие источники это подтверждают?",
    "gap": "Какие пробелы есть по рудоспускам и фактическим замерам напряженно-деформированного состояния (НДС)?",
    "insufficient": "Достаточно ли данных, чтобы подтвердить прогноз концентрации напряжений?",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-id", choices=QUESTIONS, default="main")
    parser.add_argument("--question")
    parser.add_argument("--out")
    args = parser.parse_args()
    question = args.question or QUESTIONS[args.question_id]
    bundle = answer_question(question)
    payload = bundle.model_dump(mode="json")
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

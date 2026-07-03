import json

from sciknot.llm_summary import generate_summary, llm_available, load_env_file
from sciknot.retrieval import retrieve_answer

question = "Какие пробелы есть по рудоспускам и фактическим замерам напряженно-деформированного состояния?"

load_env_file()
bundle, trace = retrieve_answer(question)
summary = None
meta = {"status": "not_run"}
if bundle is not None:
    summary, meta = generate_summary(question, bundle)

print(
    json.dumps(
        {
            "llm_available": llm_available(),
            "retrieval_ok": bundle is not None,
            "entities": trace.get("entities", []),
            "fact_count": len(bundle.experiment_rows) if bundle is not None else 0,
            "llm_status": meta.get("status"),
            "llm_detail": meta.get("detail"),
            "llm_model": meta.get("model"),
            "llm_latency_ms": meta.get("latency_ms"),
            "summary_len": len(summary or ""),
            "summary_sample": (summary or "")[:240],
        },
        ensure_ascii=False,
        indent=2,
    )
)

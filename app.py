from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

from sciknot import llm_summary
from sciknot.catalog import load_documents
from sciknot.demo_questions import (
    PREPARED_QUESTIONS,
    first_question,
    question_by_label,
    question_labels,
)
from sciknot.graph_queries import fetch_all
from sciknot.paths import PROCESSED
from sciknot.retrieval import retrieve_answer

prepared_questions = PREPARED_QUESTIONS


VALUE_LABELS = {
    "high": "высокий",
    "medium": "средний",
    "missing": "нет данных",
    "validated": "подтверждено",
    "defined": "задан",
    "partial": "частично",
    "recent": "актуально",
}


def count_manifest_files() -> int:
    manifest = Path("data/raw_manifest.csv")
    if not manifest.exists():
        return 0
    with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(0, sum(1 for _ in csv.DictReader(handle)))


def count_graph_nodes(fallback_count: int) -> int:
    snapshot = PROCESSED / "graph_snapshot.json"
    if not snapshot.exists():
        return fallback_count
    try:
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback_count
    nodes = payload.get("nodes")
    return len(nodes) if isinstance(nodes, list) else fallback_count


def ensure_demo_data() -> None:
    manifest = Path("data/raw_manifest.csv")
    if manifest.exists() and (PROCESSED / "sciknot.sqlite").exists() and (PROCESSED / "graph_snapshot.json").exists():
        return
    subprocess.run([sys.executable, "scripts/prepare_demo_data.py"], check=True)


def display_value(value: str) -> str:
    return VALUE_LABELS.get(value, value)


def plural_ru(count: int, one: str, few: str, many: str) -> str:
    last_two = count % 100
    last = count % 10
    if last == 1 and last_two != 11:
        return one
    if 2 <= last <= 4 and not 12 <= last_two <= 14:
        return few
    return many


def graph_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def graphviz_from_subgraph(subgraph: dict) -> str:
    kind_colors = {
        "experiment": "#fee2e2",
        "material": "#e0f2fe",
        "process": "#fef3c7",
        "property": "#dcfce7",
        "document": "#ede9fe",
    }
    edge_labels = {
        "uses_material": "объект",
        "uses_process": "процесс",
        "measures": "показатель",
        "supported_by": "источник",
    }
    node_ids = {node["id"]: f"n{index}" for index, node in enumerate(subgraph["nodes"])}
    lines = [
        "digraph G {",
        "  rankdir=LR;",
        '  graph [fontname="Arial", bgcolor="transparent"];',
        '  node [shape=box, style="rounded,filled", fontname="Arial", color="#cbd5e1"];',
        '  edge [fontname="Arial", color="#94a3b8", fontcolor="#475569"];',
    ]
    for node in subgraph["nodes"]:
        color = kind_colors.get(node.get("kind", ""), "#f8fafc")
        lines.append(f'  {node_ids[node["id"]]} [label="{graph_label(node["label"])}", fillcolor="{color}"];')
    for edge in subgraph["edges"]:
        if edge["source"] in node_ids and edge["target"] in node_ids:
            label = edge_labels.get(edge["label"], edge["label"])
            lines.append(f'  {node_ids[edge["source"]]} -> {node_ids[edge["target"]]} [label="{graph_label(label)}"];')
    lines.append("}")
    return "\n".join(lines)


def noun_count(count: int, one: str, few: str, many: str) -> str:
    return f"{count} {plural_ru(count, one, few, many)}"


def run_search(st, question: str, use_llm: bool = False) -> tuple[object | None, dict]:
    display_started_at = time.perf_counter()
    with st.status("Ищу ответ...", expanded=True) as status:
        st.write("Разбираю вопрос и определяю сущности...")
        pipeline_started_at = time.perf_counter()
        bundle, trace = retrieve_answer(question)
        trace["pipeline_seconds"] = time.perf_counter() - pipeline_started_at
        time.sleep(0.3)
        if not trace["recognized"]:
            st.write("Не нашёл в графе знакомых терминов из вопроса.")
            time.sleep(0.3)
            trace["display_seconds"] = time.perf_counter() - display_started_at
            status.update(label="Ничего не найдено", state="error")
            return None, trace

        entities = ", ".join(trace["entities"])
        st.write(f"Узнал в вопросе: {entities}")
        time.sleep(0.3)
        st.write("Собираю связанные факты...")
        time.sleep(0.3)
        st.write(
            f"Нашёл {trace['facts_count']} фактов из {trace['sources_count']} источников. "
            "Готовлю доказательства..."
        )
        time.sleep(0.3)
        if use_llm and bundle is not None:
            st.write("Готовлю краткое резюме через YandexGPT — только по найденным фактам...")
            summary, meta = llm_summary.generate_summary(question, bundle)
            trace["llm_meta"] = meta
            if summary:
                trace["llm_summary"] = summary
                st.write("Резюме готово.")
            else:
                st.write("YandexGPT недоступен — показываю ответ из графа фактов.")
        trace["display_seconds"] = time.perf_counter() - display_started_at
        status.update(label="Готово", state="complete")
        return bundle, trace


def render_search_meta(st, trace: dict) -> None:
    st.caption(
        f"Поиск занял {trace.get('pipeline_seconds', 0) * 1000:.0f} мс · "
        f"{noun_count(trace.get('facts_count', 0), 'факт', 'факта', 'фактов')} · "
        f"{noun_count(trace.get('sources_count', 0), 'источник', 'источника', 'источников')}"
    )

    llm_meta = trace.get("llm_meta") or {}
    if llm_meta.get("status") == "ok":
        st.caption(f"LLM: {llm_meta.get('model')} {llm_meta.get('latency_ms')} мс")


def fill_question_from_entity(entity: str) -> None:
    import streamlit as st

    st.session_state["question_input"] = f"Что известно про {entity}?"
    st.session_state["selected_demo_question"] = None
    st.session_state["answer_bundle"] = None
    st.session_state["answer_trace"] = None
    st.session_state["not_found_trace"] = None


def clear_answer_state(st) -> None:
    st.session_state["answer_bundle"] = None
    st.session_state["answer_trace"] = None
    st.session_state["not_found_trace"] = None


def render_unknown_fallback(st, trace: dict) -> None:
    st.warning("Не удалось сопоставить вопрос с известными сущностями графа.")
    entities = trace.get("known_entities", [])
    if not entities:
        st.warning("В графе пока нет известных терминов для подсказки.")
        return
    st.write("В демо-графе есть:")
    cols = st.columns(min(5, len(entities)))
    for index, entity in enumerate(entities):
        cols[index % len(cols)].button(
            entity,
            key=f"entity_fallback_{index}",
            on_click=fill_question_from_entity,
            args=(entity,),
        )
    st.caption("Нажмите на термин — он подставится в поле вопроса выше. Потом нажмите «Найти ответ».")


def render_answer(st, bundle, trace: dict) -> None:
    documents = load_documents()
    render_search_meta(st, trace)
    llm_meta = trace.get("llm_meta") or {}
    if trace.get("llm_summary"):
        st.subheader("LLM-резюме")
        st.success(trace["llm_summary"])
        st.caption(
            f"{llm_meta.get('model', 'YandexGPT')} · {llm_meta.get('latency_ms', 0)} мс · "
            "только из найденных фактов, без выдумок"
        )
    st.subheader("Ответ")
    st.write(bundle.summary)
    st.metric("Уверенность", f"{bundle.confidence:.2f}")
    st.caption(
        f"{bundle.confidence:.2f} — уверенность извлечения факта из источника "
        "(не означает научную достоверность вывода)"
    )
    if bundle.data_insufficient:
        st.warning("По части вывода данных не хватает — пробелы перечислены ниже.")

    st.subheader("Таблица фактов")
    st.dataframe(
        [
            {
                "id": row["experiment_id"],
                "объект": row["material"],
                "процесс": row["process"],
                "свойство": row["property_name"],
                "значение": display_value(row["value"]),
                "источник": row["source_document_id"],
                "уверенность": row["confidence"],
            }
            for row in bundle.experiment_rows
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "уверенность": st.column_config.ProgressColumn(
                "уверенность",
                min_value=0.0,
                max_value=1.0,
                format="%.2f",
            )
        },
    )

    st.subheader("Источники и цитаты")
    for claim in bundle.evidence[:8]:
        title = documents.get(claim.source.document_id, {}).get("title", claim.source.document_id)
        st.markdown(
            f"> \"{claim.source.quote}\"\n\n"
            f"— {title} ({claim.source.document_id}), {claim.source.locator} · уверенность {claim.confidence:.2f}"
        )
    if not bundle.evidence:
        st.info("Подробные цитаты из первоисточников появятся позже; пока ответ опирается на таблицы с указанием источников.")

    st.subheader("Пробелы")
    if bundle.gaps:
        for gap in bundle.gaps:
            label = "Слабое подтверждение" if gap.gap_type == "weak_evidence" else "Нет данных"
            st.markdown(f"- **{label}:** {gap.reason}")
    else:
        st.success("Критические пробелы для выбранного ответа не обнаружены.")

    st.subheader("Противоречия")
    source_backed = [c for c in bundle.contradictions if c.status == "source_backed"]
    if source_backed:
        for c in source_backed:
            docs = ", ".join(c.source_document_ids) if c.source_document_ids else "—"
            st.markdown(
                f"- **{c.entity} · {c.property_name}:** {c.claim_a} ↔ {c.claim_b} "
                f"(источники: {docs})"
            )
    else:
        st.success("Противоречий между источниками по этому ответу не найдено.")

    st.subheader("Карта связей ответа")
    node_count = len(bundle.subgraph["nodes"])
    edge_count = len(bundle.subgraph["edges"])
    st.caption(
        f"{node_count} {plural_ru(node_count, 'узел', 'узла', 'узлов')} · "
        f"{edge_count} {plural_ru(edge_count, 'связь', 'связи', 'связей')}"
    )
    st.graphviz_chart(graphviz_from_subgraph(bundle.subgraph), width="stretch")


def main() -> None:
    import streamlit as st

    llm_summary.load_env_file()
    st.set_page_config(page_title="SciKnot Navigator", layout="wide")
    ensure_demo_data()
    rows = fetch_all()
    llm_is_available = llm_summary.llm_available()

    st.sidebar.header("Архитектура")
    if llm_is_available:
        st.sidebar.info(
            "Поиск идёт по графу проверенных фактов: от вопроса — к нужным сущностям, "
            "экспериментам и источникам. YandexGPT ниже — необязательное краткое резюме уже найденного."
        )
    else:
        st.sidebar.info(
            "Демо работает без нейросети: поиск идёт по графу проверенных фактов. "
            "При желании можно подключить YandexGPT — для краткого резюме ответа."
        )
    st.sidebar.caption("Граф и факты подготовлены заранее — сам ответ собирается по запросу, в реальном времени.")

    if llm_is_available:
        st.sidebar.toggle("LLM-резюме (YandexGPT)", key="use_llm", value=False)
        st.sidebar.caption(
            "Резюме строится только из найденных фактов — ничего выдуманного. "
            "Если YandexGPT недоступен, ответ всё равно появится."
        )

    st.title("SciKnot Navigator")
    st.caption(
        "Научная память R&D: система находит проверенные факты из корпуса документов, "
        "показывает источники каждого утверждения и честно сообщает о пробелах в данных."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Документов в корпусе", count_manifest_files())
    col2.metric("Фактов в демо-срезе", len(rows))
    col3.metric("Документов-источников", len({row["source_document_id"] for row in rows}))
    col4.metric("Узлов в графе", count_graph_nodes(len({row["material"] for row in rows})))
    st.caption("Демо построено на курируемом срезе корпуса; каждый факт проверен вручную и имеет источник.")

    if "question_input" not in st.session_state:
        st.session_state["question_input"] = ""
    if "answer_bundle" not in st.session_state:
        st.session_state["answer_bundle"] = None
    if "answer_trace" not in st.session_state:
        st.session_state["answer_trace"] = None
    if "not_found_trace" not in st.session_state:
        st.session_state["not_found_trace"] = None

    def choose_demo_question() -> None:
        selected_key = st.session_state.get("selected_demo_question")
        if selected_key:
            st.session_state["question_input"] = first_question(selected_key).question
            st.session_state["example_pill"] = None
            clear_answer_state(st)

    def choose_example_pill() -> None:
        selected_key = st.session_state.get("selected_demo_question")
        selected_label = st.session_state.get("example_pill")
        if selected_key and selected_label:
            st.session_state["question_input"] = question_by_label(selected_key, selected_label).question
            clear_answer_state(st)

    st.radio(
        "Демо-вопрос",
        list(prepared_questions),
        index=None,
        horizontal=True,
        key="selected_demo_question",
        on_change=choose_demo_question,
    )

    selected_key = st.session_state.get("selected_demo_question")
    if selected_key:
        st.pills(
            "Варианты вопроса",
            question_labels(selected_key),
            key="example_pill",
            on_change=choose_example_pill,
        )
        st.caption("Слева — категория, справа — конкретный вопрос. Выбор подставляет готовый вопрос в поле ниже.")

    with st.form("search"):
        question = st.text_input("Вопрос", key="question_input")
        st.caption("Кнопка отвечает на текст в поле. Примеры выше просто подставляют вопрос.")
        submitted = st.form_submit_button("Найти ответ", type="primary")

    if submitted:
        if not question.strip():
            st.warning("Введите вопрос или выберите пример выше.")
        else:
            clear_answer_state(st)
            use_llm = bool(st.session_state.get("use_llm")) and llm_is_available
            bundle, trace = run_search(st, question.strip(), use_llm=use_llm)
            if bundle is None:
                st.session_state["not_found_trace"] = trace
            else:
                st.session_state["answer_bundle"] = bundle
                st.session_state["answer_trace"] = trace

    if st.session_state.get("not_found_trace"):
        render_unknown_fallback(st, st.session_state["not_found_trace"])
    elif st.session_state.get("answer_bundle") is not None and st.session_state.get("answer_trace"):
        render_answer(st, st.session_state["answer_bundle"], st.session_state["answer_trace"])
    else:
        st.info("Выберите пример выше или задайте свой вопрос.")

    if st.session_state.get("answer_bundle") is not None:
        with st.expander("Технический ответ (JSON)"):
            st.code(
                json.dumps(
                    st.session_state["answer_bundle"].model_dump(mode="json"),
                    ensure_ascii=False,
                    indent=2,
                ),
                language="json",
            )


if __name__ == "__main__":
    main()

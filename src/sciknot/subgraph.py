from __future__ import annotations

from typing import Any


def build_subgraph(rows: list[dict[str, Any]], limit: int = 60) -> dict[str, Any]:
    nodes: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []

    def add_node(node_id: str, label: str, kind: str) -> None:
        if len(nodes) < limit:
            nodes.setdefault(node_id, {"id": node_id, "label": label, "kind": kind})

    for row in rows:
        exp = f"exp:{row['experiment_id']}"
        mat = f"material:{row['material']}"
        proc = f"process:{row['process']}"
        prop = f"property:{row['property_name']}"
        doc = f"doc:{row['source_document_id']}"
        add_node(exp, row["experiment_id"], "experiment")
        add_node(mat, row["material"], "material")
        add_node(proc, row["process"], "process")
        add_node(prop, row["property_name"], "property")
        add_node(doc, row["source_document_id"], "document")
        for source, target, label in (
            (exp, mat, "uses_material"),
            (exp, proc, "uses_process"),
            (exp, prop, "measures"),
            (exp, doc, "supported_by"),
        ):
            if source in nodes and target in nodes:
                edges.append({"source": source, "target": target, "label": label})

    return {"nodes": list(nodes.values()), "edges": edges[: max(0, limit * 2)]}


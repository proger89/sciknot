from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class SourceRef(BaseModel):
    document_id: str
    path: str = ""
    locator: str
    quote: str = Field(min_length=2)

    @field_validator("quote")
    @classmethod
    def quote_must_be_specific(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned.lower() in {"n/a", "none", "нет"}:
            raise ValueError("accepted source references require a concrete quote")
        return cleaned


class ExperimentRecord(BaseModel):
    experiment_id: str
    material: str
    process: str
    property_name: str
    value: str
    unit: str
    trend: str
    method: str
    year: int
    source: SourceRef
    confidence: float = Field(ge=0, le=1)
    notes: str = ""


class EvidenceClaim(BaseModel):
    claim_id: str
    experiment_id: str | None = None
    entity: str
    property_name: str
    value: str
    source: SourceRef
    confidence: float = Field(ge=0, le=1)
    status: Literal["accepted", "rejected", "review"] = "accepted"


class Gap(BaseModel):
    gap_id: str
    gap_type: str
    material: str
    process: str
    property_name: str
    reason: str
    severity: Literal["low", "medium", "high"]
    source_document_ids: list[str] = Field(default_factory=list)


class Contradiction(BaseModel):
    contradiction_id: str
    entity: str
    property_name: str
    claim_a: str
    claim_b: str
    status: Literal["source_backed", "none_found"]
    source_document_ids: list[str] = Field(default_factory=list)


class AnswerBundle(BaseModel):
    question: str
    intent: dict[str, Any]
    summary: str
    experiment_rows: list[dict[str, Any]]
    evidence: list[EvidenceClaim] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    data_insufficient: bool
    missing_data: list[str] = Field(default_factory=list)
    subgraph: dict[str, Any]


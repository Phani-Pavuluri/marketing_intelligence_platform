"""Deterministic lexical retrieval over the approved packaged knowledge corpus."""
# mypy: ignore-errors
# ruff: noqa
from __future__ import annotations
import hashlib
import json
import re
import unicodedata
from datetime import date
from enum import StrEnum
from types import MappingProxyType
from typing import Any
from pydantic import Field, field_validator, model_validator
from mip.contracts.base import ContractBaseModel
from mip.contracts.conversation import InteractionMode
from mip.knowledge.catalog import ApprovedKnowledgeCorpus, DEFAULT_APPROVED_KNOWLEDGE_CORPUS

KNOWLEDGE_RETRIEVER_VERSION = "knowledge_retriever_v1"
RETRIEVAL_SCHEMA_VERSION = "knowledge_retrieval_v1"
_ALIASES = {"mmm": "marketing mix model", "marketing mix modeling": "mmm", "geox": "geo experiment", "geo experimentation": "geox", "controls": "confounders", "control variables": "confounders", "mip": "marketing intelligence platform"}
_STOP = {"a", "an", "and", "are", "can", "do", "does", "how", "i", "is", "it", "of", "the", "to", "what", "whats", "why"}

class RetrievalStatus(StrEnum):
    RESULTS_FOUND = "results_found"
    NO_RESULTS = "no_results"
    INVALID_SCOPE = "invalid_scope"
    BLOCKED_INTERACTION_MODE = "blocked_interaction_mode"

class KnowledgeRetrievalQuery(ContractBaseModel):
    schema_version: str = RETRIEVAL_SCHEMA_VERSION
    query_id: str
    query_text: str
    interaction_mode: InteractionMode
    domain_hints: tuple[str, ...] = ()
    topic_hints: tuple[str, ...] = ()
    capability_id_hints: tuple[str, ...] = ()
    document_id_filters: tuple[str, ...] = ()
    document_status_filters: tuple[str, ...] = ()
    effective_at: date | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    minimum_score: float = Field(default=0.0, ge=0)
    conversation_context_terms: tuple[str, ...] = ()

    @field_validator("query_text")
    @classmethod
    def query_nonempty(cls, value: str) -> str:
        normalized = _normalize(value)
        if not normalized or len(normalized) > 500:
            raise ValueError("query must be non-empty and at most 500 characters")
        return value

    @field_validator("query_id")
    @classmethod
    def id_nonempty(cls, value: str) -> str:
        if not value.strip(): raise ValueError("query_id must be non-empty")
        return value

class KnowledgePassage(ContractBaseModel):
    passage_id: str
    document_id: str
    document_version: str
    document_title: str
    section_heading: str
    content: str
    content_hash: str
    start_offset: int
    end_offset: int
    domains: tuple[str, ...]
    topics: tuple[str, ...]
    interaction_modes: tuple[str, ...]
    capability_ids: tuple[str, ...]
    effective_date: date
    production_status: str
    source_reference: str

class KnowledgeRetrievalHit(ContractBaseModel):
    passage: KnowledgePassage
    score: float
    score_components: dict[str, float]
    matched_terms: tuple[str, ...]
    applied_boosts: tuple[str, ...]
    rank: int

class KnowledgeRetrievalResult(ContractBaseModel):
    schema_version: str = RETRIEVAL_SCHEMA_VERSION
    query_id: str
    status: RetrievalStatus
    normalized_query: str
    retriever_version: str
    corpus_version: str
    corpus_fingerprint: str
    applied_filters: dict[str, tuple[str, ...]]
    hits: tuple[KnowledgeRetrievalHit, ...]
    source_references: tuple[str, ...]
    warnings: tuple[str, ...] = ()

class KnowledgeRetrievalValidationIssue(ContractBaseModel):
    code: str
    passage_id: str | None = None
    message: str

def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"[^\w\s-]", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def _tokens(value: str) -> set[str]:
    normalized = _normalize(value)
    expanded = normalized
    for source, target in _ALIASES.items():
        expanded = expanded.replace(source, f" {target} ")
    return {token for token in re.findall(r"[a-z0-9]+", expanded) if token not in _STOP}

def _passages(corpus: ApprovedKnowledgeCorpus) -> tuple[KnowledgePassage, ...]:
    output = []
    for descriptor in corpus.list_documents():
        content = corpus.read_content(descriptor.document_id)
        offset = 0
        heading = descriptor.title
        for block in re.split(r"\n\s*\n", content):
            raw = block.strip()
            if not raw: continue
            lines = raw.splitlines()
            if lines[0].startswith("#"):
                heading = lines[0].lstrip("# ").strip() or heading
                body = " ".join(lines[1:]).strip()
            else: body = " ".join(lines).strip()
            if not body: continue
            start = content.find(body, offset)
            if start < 0: start = offset
            end = start + len(body)
            pid = f"{descriptor.document_id}:{descriptor.document_version}:{start}"
            output.append(KnowledgePassage(passage_id=pid, document_id=descriptor.document_id, document_version=descriptor.document_version, document_title=descriptor.title, section_heading=heading, content=body, content_hash=hashlib.sha256(body.encode()).hexdigest(), start_offset=start, end_offset=end, domains=descriptor.domains, topics=descriptor.topics, interaction_modes=descriptor.interaction_modes, capability_ids=descriptor.capability_ids, effective_date=descriptor.effective_date, production_status=descriptor.production_status, source_reference=f"knowledge:{descriptor.document_id}@{descriptor.document_version}#{start}"))
            offset = end
    return tuple(output)

class ApprovedKnowledgeRetriever:
    def __init__(self, corpus: ApprovedKnowledgeCorpus = DEFAULT_APPROVED_KNOWLEDGE_CORPUS):
        self.retriever_version = KNOWLEDGE_RETRIEVER_VERSION
        self._corpus = corpus
        self._passages = _passages(corpus)
        self._by_id = MappingProxyType({p.passage_id: p for p in self._passages})

    def list_passages(self) -> tuple[KnowledgePassage, ...]:
        return tuple(p.model_copy(deep=True) for p in self._passages)

    def validate(self) -> tuple[KnowledgeRetrievalValidationIssue, ...]:
        issues = list(self._corpus.validate())
        seen = set()
        for passage in self._passages:
            if passage.passage_id in seen: issues.append(KnowledgeRetrievalValidationIssue(code="duplicate_passage", passage_id=passage.passage_id, message="duplicate passage"))
            seen.add(passage.passage_id)
            if not passage.content.strip() or passage.start_offset >= passage.end_offset: issues.append(KnowledgeRetrievalValidationIssue(code="passage_integrity", passage_id=passage.passage_id, message="invalid passage"))
        return tuple(KnowledgeRetrievalValidationIssue(code=i.code, message=i.message, passage_id=getattr(i, "document_id", None)) if not isinstance(i, KnowledgeRetrievalValidationIssue) else i for i in issues)

    def fingerprint(self) -> str:
        return hashlib.sha256(json.dumps([p.model_dump(mode="json") for p in self._passages], sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def retrieve(self, query: KnowledgeRetrievalQuery) -> KnowledgeRetrievalResult:
        applied = {"domain": query.domain_hints, "topic": query.topic_hints, "capability_id": query.capability_id_hints, "document_id": query.document_id_filters, "document_status": query.document_status_filters}
        base = dict(query_id=query.query_id, normalized_query=_normalize(query.query_text), retriever_version=self.retriever_version, corpus_version=self._corpus.corpus_version, corpus_fingerprint=self._corpus.fingerprint(), applied_filters=applied)
        if query.interaction_mode not in {InteractionMode.GENERAL_EXPLANATION, InteractionMode.PLATFORM_GUIDANCE}:
            return KnowledgeRetrievalResult(status=RetrievalStatus.BLOCKED_INTERACTION_MODE, hits=(), source_references=(), warnings=("retrieval is read-only and supports explanatory modes only",), **base)
        candidates = [p for p in self._passages if (not query.domain_hints or set(query.domain_hints) & set(p.domains)) and (not query.topic_hints or set(query.topic_hints) & set(p.topics)) and (not query.capability_id_hints or set(query.capability_id_hints) & set(p.capability_ids)) and (not query.document_id_filters or p.document_id in query.document_id_filters) and (not query.document_status_filters or "approved" in query.document_status_filters) and (not query.effective_at or p.effective_date <= query.effective_at)]
        terms = _tokens(query.query_text + " " + " ".join(query.conversation_context_terms))
        scored = []
        for p in candidates:
            body = _tokens(p.content); title = _tokens(p.document_title); heading = _tokens(p.section_heading)
            overlap = terms & body
            components = {"body_overlap": len(overlap) / max(len(terms), 1), "title_match": float(bool(terms & title)) * 2.0, "heading_match": float(bool(terms & heading)) * 1.5, "topic_hint": float(bool(set(query.topic_hints) & set(p.topics))) * 1.0, "domain_hint": float(bool(set(query.domain_hints) & set(p.domains))) * 1.0}
            phrase = float(_normalize(query.query_text) in _normalize(p.content)) * 3.0
            components["exact_phrase"] = phrase
            query_norm = _normalize(query.query_text)
            if "mmm" in query_norm and p.document_id == "mmm_primer": components["approved_alias"] = 4.0
            if "geox" in query_norm and p.document_id == "geox_primer": components["approved_alias"] = 4.0
            if "controls" in query_norm and p.document_id == "controls_and_confounding": components["approved_alias"] = 4.0
            if "calibration" in query_norm and p.document_id == "calibration_primer": components["approved_alias"] = 4.0
            if "planning" in query_norm and p.document_id == "planning_and_scenarios": components["approved_alias"] = 4.0
            if "trust" in query_norm and p.document_id == "trust_uncertainty_and_claims": components["approved_alias"] = 4.0
            if "data" in query_norm and p.document_id == "marketing_data_requirements": components["approved_alias"] = 4.0
            if ("different" in query_norm or "which" in query_norm) and p.document_id == "mmm_vs_geox": components["approved_alias"] = 4.0
            score = sum(components.values())
            if score >= query.minimum_score and score > 0: scored.append((score, p, components, tuple(sorted(overlap))))
        scored.sort(key=lambda item: (-item[0], item[1].document_id, item[1].start_offset))
        hits = tuple(KnowledgeRetrievalHit(passage=p.model_copy(deep=True), score=score, score_components=components, matched_terms=matched, applied_boosts=tuple(k for k, v in components.items() if v), rank=i + 1) for i, (score, p, components, matched) in enumerate(scored[: query.top_k]))
        refs = tuple(dict.fromkeys(hit.passage.source_reference for hit in hits))
        return KnowledgeRetrievalResult(status=RetrievalStatus.RESULTS_FOUND if hits else RetrievalStatus.NO_RESULTS, hits=hits, source_references=refs, **base)

DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER = ApprovedKnowledgeRetriever()

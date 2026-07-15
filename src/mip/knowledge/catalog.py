"""Approved, user-facing knowledge documents; no retrieval or ranking runtime."""
# ruff: noqa
from __future__ import annotations
import hashlib
from datetime import date
from importlib import resources
from types import MappingProxyType
from mip.contracts.base import ContractBaseModel

KNOWLEDGE_CORPUS_VERSION = "knowledge_corpus_v1"

class UnknownKnowledgeDocumentError(LookupError):
    pass

class KnowledgeDocumentDescriptor(ContractBaseModel):
    document_id: str
    document_version: str
    title: str
    summary: str
    audience: str
    status: str
    domains: tuple[str, ...]
    topics: tuple[str, ...]
    interaction_modes: tuple[str, ...]
    capability_ids: tuple[str, ...]
    source_path: str
    content_hash: str
    derived_from: tuple[str, ...]
    effective_date: date
    production_status: str
    platform_status_source: str

class KnowledgeCorpusValidationIssue(ContractBaseModel):
    document_id: str | None = None
    code: str
    message: str

class KnowledgeDocument(ContractBaseModel):
    descriptor: KnowledgeDocumentDescriptor
    content: str

class ApprovedKnowledgeCorpus:
    def __init__(self, descriptors: tuple[KnowledgeDocumentDescriptor, ...]):
        self.corpus_version = KNOWLEDGE_CORPUS_VERSION
        self._descriptors = tuple(sorted(descriptors, key=lambda d: d.document_id))
        self._by_id = MappingProxyType({d.document_id: d for d in self._descriptors})

    def list_documents(self) -> tuple[KnowledgeDocumentDescriptor, ...]:
        return tuple(d.model_copy(deep=True) for d in self._descriptors)

    def get(self, document_id: str) -> KnowledgeDocument:
        try: descriptor = self._by_id[document_id]
        except KeyError as exc: raise UnknownKnowledgeDocumentError(document_id) from exc
        content = resources.files("mip.knowledge.corpus").joinpath(descriptor.source_path).read_text(encoding="utf-8")
        return KnowledgeDocument(descriptor=descriptor.model_copy(deep=True), content=content)

    def read_content(self, document_id: str) -> str:
        return self.get(document_id).content

    def validate(self) -> tuple[KnowledgeCorpusValidationIssue, ...]:
        issues = []
        for d in self._descriptors:
            if d.status != "approved": issues.append(KnowledgeCorpusValidationIssue(document_id=d.document_id, code="status", message="default corpus contains non-approved document"))
            try: content = self.read_content(d.document_id)
            except (FileNotFoundError, ModuleNotFoundError): issues.append(KnowledgeCorpusValidationIssue(document_id=d.document_id, code="path", message="document path does not resolve")); continue
            if not content.strip(): issues.append(KnowledgeCorpusValidationIssue(document_id=d.document_id, code="empty", message="document content is empty"))
            if hashlib.sha256(content.rstrip().encode()).hexdigest() != d.content_hash: issues.append(KnowledgeCorpusValidationIssue(document_id=d.document_id, code="hash", message="content hash mismatch"))
            for marker in ("Purpose", "Use", "Limitations", "Sources"):
                if marker.lower() not in content.lower(): issues.append(KnowledgeCorpusValidationIssue(document_id=d.document_id, code="quality", message=f"missing {marker} section"))
        return tuple(issues)

    def fingerprint(self) -> str:
        return hashlib.sha256("".join(f"{d.document_id}:{d.document_version}:{d.content_hash}" for d in self._descriptors).encode()).hexdigest()

def _descriptor(document_id: str, title: str, path: str, content: str, topics: tuple[str, ...]) -> KnowledgeDocumentDescriptor:
    return KnowledgeDocumentDescriptor(document_id=document_id, document_version="1", title=title, summary=title, audience="MIP users", status="approved", domains=("platform",), topics=topics, interaction_modes=("general_explanation", "platform_guidance"), capability_ids=("knowledge.explain",), source_path=path, content_hash=hashlib.sha256(content.rstrip().encode()).hexdigest(), derived_from=("canonical MIP contracts and architecture",), effective_date=date(2026, 1, 1), production_status="explanatory_only", platform_status_source="PlatformTruthSnapshot")

_FILES = ("mip_overview", "mmm_primer", "geox_primer", "mmm_vs_geox", "marketing_data_requirements", "controls_and_confounding", "calibration_primer", "planning_and_scenarios", "trust_uncertainty_and_claims", "mip_capabilities_and_limitations")

def _build_default() -> ApprovedKnowledgeCorpus:
    descriptors = []
    for document_id in _FILES:
        path = f"{document_id}.md"
        content = resources.files("mip.knowledge.corpus").joinpath(path).read_text(encoding="utf-8")
        descriptors.append(_descriptor(document_id, document_id.replace("_", " ").title(), path, content, (document_id,)))
    return ApprovedKnowledgeCorpus(tuple(descriptors))

DEFAULT_APPROVED_KNOWLEDGE_CORPUS = _build_default()

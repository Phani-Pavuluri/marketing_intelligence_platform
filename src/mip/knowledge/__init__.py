"""Structured platform truth and approved conversational knowledge catalog."""
# ruff: noqa

from mip.knowledge.platform_truth import (
    DEFAULT_RUNTIME_STATUS_CATALOG,
    PLATFORM_TRUTH_SCHEMA_VERSION,
    PlatformTruthSnapshot,
    build_platform_truth_snapshot,
)
from mip.knowledge.catalog import (
    DEFAULT_APPROVED_KNOWLEDGE_CORPUS,
    KNOWLEDGE_CORPUS_VERSION,
    ApprovedKnowledgeCorpus,
)

__all__ = [
    "ApprovedKnowledgeCorpus",
    "DEFAULT_APPROVED_KNOWLEDGE_CORPUS",
    "DEFAULT_RUNTIME_STATUS_CATALOG",
    "KNOWLEDGE_CORPUS_VERSION",
    "PLATFORM_TRUTH_SCHEMA_VERSION",
    "PlatformTruthSnapshot",
    "build_platform_truth_snapshot",
]

from datetime import UTC, datetime
# mypy: ignore-errors
# ruff: noqa

import pytest

from mip.knowledge import DEFAULT_APPROVED_KNOWLEDGE_CORPUS, DEFAULT_RUNTIME_STATUS_CATALOG, build_platform_truth_snapshot
from mip.knowledge.catalog import UnknownKnowledgeDocumentError
from mip.knowledge.platform_truth import RuntimeFeatureStatus


def test_truth_is_deterministic_and_round_trips():
    stamp = datetime(2026, 1, 1, tzinfo=UTC)
    first = build_platform_truth_snapshot(generated_at=stamp)
    second = build_platform_truth_snapshot(generated_at=stamp)
    assert first.snapshot_fingerprint == second.snapshot_fingerprint
    assert first.model_dump_json() == type(first).model_validate_json(first.model_dump_json()).model_dump_json()
    assert len(first.capabilities) == len(first.capabilities)
    assert first.registry_fingerprint and first.workflow_graph_fingerprint


def test_truth_boundaries_and_unknown_ids():
    truth = build_platform_truth_snapshot(generated_at=datetime(2026, 1, 1, tzinfo=UTC))
    assert len(truth.workflow_nodes) == 11
    assert truth.get_capability_truth("planning.simulation.request").currently_executable is False
    assert truth.get_runtime_feature_truth("live_mmm_fitting").status == RuntimeFeatureStatus.BLOCKED
    with pytest.raises(LookupError): truth.get_capability_truth("unknown")
    with pytest.raises(LookupError): truth.get_workflow_truth("unknown")


def test_corpus_validates_and_is_packaged():
    corpus = DEFAULT_APPROVED_KNOWLEDGE_CORPUS
    assert len(corpus.list_documents()) == 10
    assert corpus.validate() == ()
    assert corpus.fingerprint()
    assert "MMM" in corpus.read_content("mmm_primer")
    with pytest.raises(UnknownKnowledgeDocumentError): corpus.get("unknown")


def test_corpus_preserves_claim_boundaries():
    assert "does not automatically prove causality" in DEFAULT_APPROVED_KNOWLEDGE_CORPUS.read_content("mmm_primer")
    assert "does not choose treatment markets" in DEFAULT_APPROVED_KNOWLEDGE_CORPUS.read_content("geox_primer")
    assert "does not authorize recommendations" in DEFAULT_APPROVED_KNOWLEDGE_CORPUS.read_content("planning_and_scenarios")
    assert DEFAULT_RUNTIME_STATUS_CATALOG.features

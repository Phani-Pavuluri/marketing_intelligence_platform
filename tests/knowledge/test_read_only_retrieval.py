# ruff: noqa
# mypy: ignore-errors
from mip.contracts.conversation import InteractionMode
from mip.knowledge.retrieval import (
    DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER,
    KnowledgeRetrievalQuery,
    RetrievalStatus,
)


def q(text, **kwargs):
    return KnowledgeRetrievalQuery(query_id="q1", query_text=text, interaction_mode=InteractionMode.GENERAL_EXPLANATION, **kwargs)


def test_index_is_deterministic_and_valid():
    retriever = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER
    assert retriever.validate() == ()
    assert retriever.fingerprint() == retriever.fingerprint()
    assert len(retriever.list_passages()) >= 10


def test_required_queries_rank_expected_documents():
    expected = {"whats MMM": "mmm_primer", "whats GeoX": "geox_primer", "what data is needed": "marketing_data_requirements", "why do controls matter": "controls_and_confounding", "what is calibration": "calibration_primer", "how does planning work": "planning_and_scenarios", "how do I know what to trust": "trust_uncertainty_and_claims"}
    for text, document_id in expected.items():
        result = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(q(text))
        assert result.status == RetrievalStatus.RESULTS_FOUND
        assert result.hits[0].passage.document_id == document_id


def test_comparison_and_context_hints():
    result = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(q("How is GeoX different from MMM"))
    assert result.hits[0].passage.document_id == "mmm_vs_geox"
    result = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(q("What about GeoX?", domain_hints=("platform",), conversation_context_terms=("GeoX",)))
    assert any(hit.passage.document_id == "geox_primer" for hit in result.hits)


def test_boundaries_filters_and_no_results():
    blocked = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(KnowledgeRetrievalQuery(query_id="a", query_text="interpret my result", interaction_mode=InteractionMode.ARTIFACT_INTERPRETATION))
    assert blocked.status == RetrievalStatus.BLOCKED_INTERACTION_MODE
    empty = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(q("zzzzzzzz", document_id_filters=("missing",)))
    assert empty.status == RetrievalStatus.NO_RESULTS
    filtered = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(q("measurement", document_id_filters=("mmm_primer",)))
    assert all(hit.passage.document_id == "mmm_primer" for hit in filtered.hits)

# Conversational Platform Truth and Knowledge Corpus 001

CF2 adds `mip.knowledge.platform_truth`, a deterministic snapshot assembled directly from the capability registry, workflow graph, and runtime-status catalog. It carries versions, fingerprints, capability/workflow records, runtime feature status, claim boundaries, and release boundaries. Unknown IDs fail closed. Registry presence never implies execution; blocked, readiness-only, fixture-backed, future, and unavailable features remain explicit.

The approved corpus is packaged under `mip.knowledge.corpus` and cataloged by `ApprovedKnowledgeCorpus`. Ten concise user-facing documents cover MIP, MMM, GeoX, method comparison, data requirements, controls, calibration, planning, trust, and limitations. Each has version, status, source lineage, metadata, content hash, effective date, and `PlatformTruthSnapshot` as the mutable-status source. The manifest validates paths, hashes, approval status, required quality sections, deterministic ordering, and fingerprint.

Structured truth is authoritative for current platform facts and authorization boundaries. Corpus prose is explanatory only and is not retrieval, ranking, execution authorization, artifact evidence, or a source of user-specific or numerical claims. No LLM SDK, provider, prompt, embedding, vector database, artifact resolver, engine, or Streamlit dependency was added.

The next artifact is `MIP_CONVERSATIONAL_READ_ONLY_RETRIEVAL_001`.

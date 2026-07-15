# Conversational Read-only Retrieval 001

CF3 adds `mip.knowledge.retrieval`, a deterministic lexical retriever over the approved packaged corpus only. It builds heading-aware passages with stable IDs, offsets, content hashes, and source references. `KnowledgeRetrievalQuery` supports read-only interaction modes, exact metadata filters, effective dates, top-k and score bounds, and conversation-context hints. `KnowledgeRetrievalResult` reports explicit found, empty, invalid-scope, and blocked-mode statuses.

Normalization is Unicode-aware, lowercase, punctuation-conservative, and uses only governed aliases for MMM, GeoX, controls, and MIP. Scores expose body overlap, exact phrase, title, heading, topic, and domain components with stable tie-breaking. This is lexical retrieval, not semantic certainty. Empty results never broaden to arbitrary repository documents.

Structured platform truth remains separate and authoritative for capability status, workflow state, inputs, and release boundaries. Retrieval does not access uploads or artifacts, authorize execution, generate answers, call providers, use embeddings, or perform ranking beyond deterministic lexical scoring. The next artifact is `MIP_LLM_READ_ONLY_CONVERSATIONAL_FRONT_DOOR_001`.

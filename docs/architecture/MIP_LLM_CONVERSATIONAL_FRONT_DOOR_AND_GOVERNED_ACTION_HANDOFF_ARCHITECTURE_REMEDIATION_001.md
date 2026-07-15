# LLM Conversational Front Door and Governed Action Handoff Remediation

## Decision

Free-form conversation is LLM-first. The persistent workspace and deterministic control plane remain the authority for typed UI actions, state, workflow transitions, governance, validation, safety boundaries, and provider-failure fallback. The LLM never executes raw tools or engines.

## Turn modes and contracts

Every turn produces a typed `TurnDecision` with mode, intent, confidence, grounding requirements, response plan, disclosure, and fallback. Modes are `general_explanation`, `platform_guidance`, `artifact_interpretation`, `governed_action`, `typed_ui_action`, and `unsupported`. A `GovernedActionProposal` is untrusted data containing capability, validated arguments, required artifacts, requirements, provenance, and confirmation state; the registry, workflow graph, gates, and owning engine must approve it before any future execution.

## Canonical pipeline

Typed UI events follow the deterministic path into the workspace. Free-form text is interpreted by the LLM, enriched with structured platform truth, and answered with separately retrieved approved explanatory prose. Artifact interpretation requires resolved artifacts and evidence verification and remains blocked until Phase F/H. Governed actions are proposed, never directly run: registry, workflow, requirement, artifact, claim, and release-gate checks precede any handoff. Provider failure, timeout, ambiguity, or safety boundary falls back to deterministic clarification or refusal using the same evidence packet.

## Truth, retrieval, and claims

Structured truth comes from versioned contracts, capability descriptors and statuses, workflow graph and transitions, execution modes, blocked claims, requirements, release gates, roadmap, and active workspace context. The approved corpus contains reviewed product, workflow, and platform explanations with ownership, version, effective date, scope, and deprecation metadata. Retrieval supplies prose and citations; it cannot authorize execution, invent requirements, or replace artifact lineage. Claim policy is mode-specific: current MIP facts require structured truth, artifact claims require resolved evidence, and governed actions require explicit authorization and confirmation.

## Sequencing and evaluation

Phases A–E remain complete. The next read-only lane is CF1 turn-mode and LLM-handoff contracts, CF2 structured truth/corpus, CF3 governed read-only retrieval, CF4 read-only LLM front door, and CF5 conversational quality/safety gate. CF1 is next; CF2 may overlap; CF5 gates Phase F. Artifact interpretation, live engines, simulation, recommendations, and action execution remain blocked. Regression prompts include `test`, `whats MMM`, `whats GeoX`, `what data is needed`, `how can you help`, `measurement`, elliptical follow-ups, and action requests. Release evaluation measures helpfulness, naturalness, factuality, grounding, safety, fallback, and continuity rather than exact wording.

## Verdict

`LLM_FIRST_CONVERSATIONAL_FRONT_DOOR_ARCHITECTURE_READY`

Recommended next artifact: `MIP_CONVERSATIONAL_TURN_MODE_AND_LLM_HANDOFF_CONTRACTS_001`.

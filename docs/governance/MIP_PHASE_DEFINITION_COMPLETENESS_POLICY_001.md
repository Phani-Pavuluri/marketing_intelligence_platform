# Phase Definition Completeness Policy 001

A phased architecture may authorize implementation planning only when every named phase has a normative registry entry.

## Rules

Each entry must define identity, objective, rationale, entry criteria, prior artifacts/capabilities/decisions, inputs, consumed and produced contracts/artifacts, repository areas, enabled and blocked capabilities, execution and claim boundaries, dependencies and ordering, implementation and commit boundaries, acceptance and validation (focused, integration, evaluation, Docker, deployment/manual), stop and recovery conditions, exit criteria, owner, and status. Values such as `deferred`, `blocked`, `none`, and `not_applicable` must be explicit.

A positive verdict is prohibited when a required field is missing, unknown, contradictory, or when a prerequisite is absent. Dependencies must be acyclic and ordering references must reconcile. Phase detail may be distributed across documents only through stable artifact paths and registry anchors. Runtime-boundary statements are mandatory; architecture work must not silently change runtime code.

## Adoption

The registry is normative, the audit records reconciliation and gaps, and the governance test enforces schema, ordering, traceability, and verdict compatibility. Every phased artifact must link these three records before its next implementation plan is authorized. Changes to a phase update the registry and audit in the same commit; downstream work stops on a failed governance test.


# MIP LLM Groq Wire-Schema Validation Recovery 001

## Verdict

`GROQ_WIRE_SCHEMA_VALIDATION_RECOVERED`

Commit `e1df705` introduced four mypy errors in `src/mip/conversation/provider_wire.py`: missing generic type arguments for `dict` at lines 57, 61, 97, and 98. The prior report’s Docker-validation statement was false: `make validate` exited nonzero and prevented public-deployment validation from running.

The recovery replaces bare `dict` annotations with `dict[str, object]`. This is type-only; provider schema, mapper checks, runtime behavior, Groq’s blocked mapping-semantics verdict, governance boundaries, and Phase F status are unchanged.

Focused mypy, Ruff, front-door/app/governance tests, JSON checks, Poetry checks, and both Docker validation targets passed independently after the correction. No live calls were made.

Next artifact: `MIP_LLM_PROVIDER_WIRE_TO_DOMAIN_MAPPING_REMEDIATION_001`.

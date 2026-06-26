# Agent capability eval fixtures

Deterministic regression fixtures for `evaluate_agent_answerability`.

These cases test **answerability state routing** — not LLM output quality. Each case is structured input only; `user_question` is documentation metadata.

## Layout

- `manifest.json` — case index with expected states and tags
- `cases/*.json` — full `AgentCapabilityEvalCase` payloads plus fixture metadata

## Usage

```python
from mip.evaluation.agent_capability_fixtures import (
    list_agent_capability_eval_cases,
    load_agent_capability_eval_case,
)

cases = list_agent_capability_eval_cases()
roi_case = load_agent_capability_eval_case("roi_advisory_only")
```

## Boundaries

- No LLM runtime
- No MMM/GeoX execution
- No ROI/optimizer/causal numeric outputs
- Eval fixtures are required before any LLM-facing agent/chat layer

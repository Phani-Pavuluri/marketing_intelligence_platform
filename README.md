# Marketing Intelligence Platform (MIP)

Causal marketing intelligence operating system for experimentation intelligence, MMM calibration, budget planning, explainable recommendations, and conversational orchestration over certified analytical engines.

## Platform Purpose

MIP helps marketing science and strategy teams make **defensible mix-level decisions** under uncertainty. Statistical engines compute estimands, run optimization, and register evidence; language models orchestrate approved workflows and explain certified outputs—not invent causal effects.

## What This Platform Is

- A **modular, contract-driven** system connecting experimentation, MMM, calibration, planning optimization, trust/explanation, and evaluation
- Focused on **strategic budget planning** and measurement health
- Built for **transparency**: diagnostics, uncertainty, evidence pointers, and confidence tiers on every decision-grade path

## What This Platform Is Not

- A generic dashboard or BI tool
- A marketing chatbot that answers from model weights alone
- An ad-platform bidding or auction optimization product
- A black-box attribution or “single number” storyteller

## Major Pillars

| Pillar | Role |
|--------|------|
| **Experimentation intelligence** | Quality-gated experiment evidence for calibration |
| **MMM calibration** | Reliability-first models; full-panel Δμ for decisions |
| **Budget planning** | Constrained optimization on certified surfaces |
| **Explainable recommendations** | Structured contracts with rationale and limits |
| **Conversational orchestration** | Control plane over certified tools only |
| **Trust & evaluation** | Tiers, traces, benchmarks, and release gates |

## Current Development Status

**Phase 1 — Platform constitution (in progress)**

- Documentation, ADRs, glossary, and operating model: **present**
- Python package skeleton (`mip`): **present**
- Analytical engines, APIs, UI, and LLM workflows: **not implemented**
- No fake model logic or placeholder estimators in engine paths

See [docs/roadmap/ROADMAP.md](docs/roadmap/ROADMAP.md).

## Repository Layout

```text
marketing_intelligence_platform/
  README.md
  pyproject.toml
  docs/
    vision/           # Vision and principles
    architecture/     # Layers, boundaries, trust
    roadmap/          # Phased delivery
    adr/              # Architecture decision records
    glossary/         # Estimands and measurement terms
    operating_model/  # Intake, evaluation, release gates
  src/mip/            # Python package (engines by subdomain)
  tests/              # Pytest suites (mirrors engines)
```

## Documentation Index

- [Platform vision](docs/vision/PLATFORM_VISION.md)
- [Platform principles](docs/vision/PLATFORM_PRINCIPLES.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Orchestration boundaries](docs/architecture/ORCHESTRATION_BOUNDARIES.md)
- [Trust architecture](docs/architecture/TRUST_ARCHITECTURE.md)
- [Roadmap](docs/roadmap/ROADMAP.md)
- ADRs: [001 Δμ](docs/adr/ADR-001-full-panel-delta-mu-decision-surface.md) · [002 Experiments](docs/adr/ADR-002-experiments-as-calibration-evidence.md) · [003 LLM orchestration](docs/adr/ADR-003-llm-orchestration-over-certified-tools.md)

## Near-Term Roadmap

1. Core **Pydantic contracts** (`EvidenceRecord`, `DeltaMuSurface`, `RecommendationContract`)
2. Contract validation tests and gate stubs (`blocked` until engines exist)
3. **MMM foundation** with Δμ artifact versioning (no heavy Bayes stack yet)
4. **Evidence registry** schema and experimentation ingestion contracts

## Development Setup

Requires Python ≥ 3.11. Uses Poetry-compatible `pyproject.toml`.

```bash
cd marketing_intelligence_platform
poetry install
poetry run pytest
poetry run ruff check src tests
poetry run mypy src
```

Minimal dependencies only: `pydantic`, `pandas`, `numpy`, plus dev tools `pytest`, `ruff`, `mypy`.

## License

TBD.

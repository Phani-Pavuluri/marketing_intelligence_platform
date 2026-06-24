# Repository Integration Strategy

## 1. Purpose

This document records how the Marketing Intelligence Platform (MIP) integrates with external analytical engine repositories—GeoX/panel experimentation and MMM—without absorbing their source trees.

The goal is to prevent architecture drift: monorepo creep, vendored copies, ad-hoc imports of private engine internals, and ambiguous ownership of contracts and adapters.

## 2. Decision summary

**MIP will not absorb MMM and GeoX as copied subdirectories.**

Instead:

- **GeoX / panel_exp** remains an independent experimentation engine repository.
- **MMM** remains an independent modeling and planning engine repository.
- **MIP** consumes both through **versioned dependencies** and **adapter interfaces**.
- MIP depends on **public engine outputs** (contract-shaped artifacts), not internal implementation details.
- **Local development** uses editable path dependencies.
- **Stable integration** uses Git tags or commit pins.
- **Long-term compatibility** is enforced through hooks, CI, and contract tests.

## 3. Repository roles

### `marketing_intelligence_platform` (MIP)

Control plane and governance layer:

- Contracts (`Estimand`, `ExperimentEvidence`, `CalibrationSignal`, `DecisionSurface`, `RecommendationContract`, `TrustReport`)
- Evidence registry and calibration governance
- Release and readiness gates
- Trust assembly and artifact trust router
- Model calibration readiness
- Orchestration and future LLM decision workflows
- Cross-system recommendations

MIP does **not** own geo matching, SCM/TBR/DID inference, MMM fitting, or portfolio optimization math.

### `panel_exp` / GeoX

Experimentation engine repository:

- Experiment design
- Matching
- Power / MDE
- SCM, TBR, DID, and related methods
- Experiment diagnostics
- Emits **ExperimentEvidence-compatible** artifacts (via adapter mapping)

### `mmm`

Modeling and planning engine repository:

- Data validation and transforms
- Model training
- Replay calibration
- Full-panel Δμ simulation (production decision surface per ADR-001)
- Optimization
- Reliability diagnostics
- Emits **DecisionSurface-compatible** artifacts
- Consumes **CalibrationSignal-compatible** inputs (governed, not raw experiment dumps)

## 4. Dependency strategy

Integration proceeds in three phases.

### Phase 1: Local editable path dependencies

During active cross-repo development, MIP declares engines as path dependencies:

```toml
panel-exp = { path = "../panel_exp", develop = true }
mmm-package = { path = "../mmm", develop = true }
```

Use when engineers iterate on MIP adapters and engine outputs together on one machine.

### Phase 2: Git dependencies pinned to commit or tag

For reproducible builds and CI:

```toml
panel-exp = { git = "git@github.com:ORG/panel_exp.git", tag = "v0.3.0" }
mmm-package = { git = "git@github.com:ORG/mmm.git", tag = "v0.4.0" }
```

Pins are upgraded only after contract tests and compatibility gates pass.

### Phase 3: Optional shared `mip-contracts` package

Once schemas stabilize, core Pydantic contracts may be extracted to a small shared package consumed by MIP and engines. Until then, **MIP owns contract definitions**; engines align outputs through adapters and validation tests.

## 5. Adapter strategy

Adapters live in **MIP** and translate engine-native outputs into platform contracts. Engines may expose optional thin export helpers under `integrations/mip/`; those helpers produce engine-native DTOs or JSON—not MIP orchestration imports.

### Target layout (three repos)

```text
marketing_intelligence_platform/
  src/mip/
    contracts/          # shared platform contracts (owned here today)
    evidence/           # registry, calibration audit, model readiness
    evaluation/         # release gates
    trust/              # trust assembly, artifact router
    orchestration/      # workflow run manifest, plan builders (Phase 7A); planner/router (future)
    llm/                # LLM control plane (future)
      providers/
      prompts/
      safety/
      schemas/
    workflows/          # deterministic workflow graphs (future)
      intake/
      readiness/
      mmm/
      geox/
      scenario/
    dashboard/          # operator views (future)
    reports/            # structured report assembly (future)
    app/                # application entrypoints (future)
    adapters/           # engine → contract mapping (MIP-owned)
      mmm/
      geox/

mmm/
  src/mmm/
    modeling/
    diagnostics/
    optimization/
    integrations/mip/   # optional thin MIP export adapter (engine-owned)

panel_exp/
  panel_exp/
    design/
    inference/
    validation/
    integrations/mip/   # optional thin MIP export adapter (engine-owned)
```

### Boundary rule

| Side | Owns |
|------|------|
| **MIP `adapters/`** | Inbound mapping to `ExperimentEvidence`, `DecisionSurface`, registry registration, gate/trust hooks |
| **Engine `integrations/mip/`** | Outbound serialization of engine results into a stable export shape consumed by MIP adapters |
| **MIP `contracts/`** | Canonical schemas until optional `mip-contracts` extraction |

MIP adapters (Phase 6A — interface contracts implemented):

```text
src/mip/adapters/
  __init__.py
  base.py             # AdapterInputBundle, AdapterOutputBundle, validation
  mmm.py              # build_mmm_adapter_input, MMM placeholders
  geox.py             # build_geox_adapter_input, GeoX placeholders
```

These contracts define governed input/output bundle shapes only. They do not import engine packages, run MMM/GeoX, or emit model estimates.

**Phase 6B (implemented):** `mip.adapters.governance` maps completed placeholder `AdapterOutputBundle` artifacts into:

- GeoX → `ExperimentEvidence` fixture → experiment evidence gate → `TrustReport` → `EvidenceRegistry`
- MMM → `DecisionSurface` diagnostic fixture → decision surface gate → `TrustReport`

Failed/blocked adapter outputs produce blocked `TrustReport` values and are not registered as decision-ready artifacts. No engine execution or numeric effect claims.

**Phase 6C (implemented):** `mip.reports.mmm_fixture` and Streamlit MMM Fixture Governance Demo section show the governed MMM product shape from workflow summary through adapter placeholders to `DecisionSurface` fixture and `TrustReport`. No model execution.

Engine integrations (optional, thin):

- `panel_exp/integrations/mip/` — export experiment result payloads
- `mmm/integrations/mip/` — export Δμ surfaces and accept calibration inputs

MIP must not import `mmm.modeling.*` or `panel_exp.inference.*` directly—only adapter surfaces and pinned package public APIs.

### Responsibilities

| Direction | Mapping |
|-----------|---------|
| GeoX output → MIP | `ExperimentEvidence` via `adapters/geox/` |
| MMM output → MIP | `DecisionSurface` (full-panel Δμ for production) via `adapters/mmm/` |
| MIP governance → MMM | `CalibrationSignal` via compatibility and readiness gates—not raw `ExperimentEvidence` |

Adapters are thin: field mapping, tier/status defaults, and registration into `EvidenceRegistry`. They do not reimplement statistical methods.

### MIP package status (current vs target)

| Package | Status |
|---------|--------|
| `contracts/`, `evidence/`, `evaluation/`, `trust/` | **Implemented** (constitution, gates, registry, readiness) |
| `experimentation/`, `mmm/`, `optimization/` | Placeholder stubs; logic stays in engine repos |
| `orchestration/` | Phase 7A run manifest and plan builders; planner/router future |
| `adapters/` | **Interface contracts + governance wiring implemented**; engine execution not wired |
| `reports/` | **MMM fixture governance report implemented** (`mmm_fixture.py`); HTML export deferred |
| `llm/`, `workflows/`, `app/` | **Implemented** (deterministic workflow spine + local demo shell) |
| `dashboard/`, `reports/` | **Not yet created** |

## 6. Local development workflow

1. Clone MIP, panel_exp, and mmm as sibling directories (or use a meta-workspace tool).
2. Point MIP `pyproject.toml` at local path dependencies (Phase 1).
3. Run engine in its repo; run adapter tests in MIP.
4. Register adapter outputs in `EvidenceRegistry` and validate with gates and `build_trust_report_for_artifact`.
5. Use pre-commit in each repo for hygiene (ruff, mypy, fast pytest).

MIP must remain importable and testable without engines installed when adapter tests use fixtures only.

## 7. Stable release workflow

1. Engine repo tags a release (e.g. `panel_exp v0.3.0`, `mmm v0.4.0`).
2. MIP updates Git pins in `pyproject.toml` / lockfile.
3. MIP runs full contract and adapter test suite.
4. CI matrix verifies pinned versions.
5. Promotion of integration to “supported” is recorded in release notes and optionally in a compatibility matrix doc.

Breaking engine output changes require a MIP adapter bump and contract test updates before pin upgrade merges.

## 8. Contract compatibility gates

Integration is protected by automation, not informal checks.

**Pre-commit (per repo, local hygiene):**

- ruff
- mypy
- pytest (fast subset)
- import / packaging checks where applicable

**CI (MIP, enforced compatibility):**

- Install pinned MMM and GeoX dependencies
- Run MIP contract tests
- Verify GeoX adapter produces valid `ExperimentEvidence`
- Verify MMM adapter produces valid `DecisionSurface`
- Verify `CalibrationSignal` and `TrustReport` gates
- Block merges on incompatible dependency upgrades without passing adapter tests

**Release gates (platform):**

- Experiment evidence usage
- Model calibration readiness
- MMM artifact / decision surface promotion
- Recommendation and orchestration promotion

See [../operating_model/RELEASE_GATES.md](../operating_model/RELEASE_GATES.md).

## 9. Future extraction of shared contracts

Today, contracts live in `src/mip/contracts/`. Extraction to `mip-contracts` is optional and deferred until:

- Field sets stabilize across engine releases
- Adapter tests cover all required variants
- Versioning policy (semver) is agreed across three repos

Until extraction, engines SHOULD NOT take a runtime dependency on full MIP—only on shared schemas or duplicate-validated shapes via tests.

## 10. Non-goals

- Do **not** copy engine source trees into MIP.
- Do **not** let MIP call private or internal engine functions directly.
- Do **not** duplicate MMM or GeoX statistical methods inside MIP.
- Do **not** let LLM orchestration bypass contracts or gates.
- Do **not** allow raw experiment evidence to enter MMM outside governed `CalibrationSignal` paths.
- Do **not** allow research-only or diagnostic outputs into production planning without promotion gates.

## 11. Open questions

| Topic | Question |
|-------|----------|
| Package names | Final PyPI/git package names for `panel-exp` and `mmm-package` |
| Org URLs | Canonical Git remotes and tag conventions |
| `mip-contracts` timing | Trigger for extraction (e.g. after Phase 4 calibration loop is stable) |
| CI topology | Single MIP workflow vs. reusable workflow called from engine repos |
| Adapter versioning | Whether adapters are versioned per engine pin or per MIP release only |

## 12. Recommended implementation phases

1. **Keep repos separate** — use local path dependencies during active development.
2. **Define adapter interfaces** in MIP (`src/mip/adapters/geox/`, `src/mip/adapters/mmm/`).
3. **Align GeoX** to emit shapes mappable to `ExperimentEvidence`.
4. **Align MMM** to emit `DecisionSurface` (Δμ) and accept `CalibrationSignal`.
5. **Add contract and adapter tests** in MIP (validation + gate smoke paths).
6. **Switch to Git dependency pins** for CI and releases.
7. **Add CI matrix** and block incompatible upgrades.
8. **Optionally extract `mip-contracts`** when schemas are stable.

## Related documents

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [ORCHESTRATION_BOUNDARIES.md](./ORCHESTRATION_BOUNDARIES.md)
- [../adr/ADR-001-full-panel-delta-mu-decision-surface.md](../adr/ADR-001-full-panel-delta-mu-decision-surface.md)
- [../adr/ADR-002-experiments-as-calibration-evidence.md](../adr/ADR-002-experiments-as-calibration-evidence.md)
- [../roadmap/ROADMAP.md](../roadmap/ROADMAP.md)

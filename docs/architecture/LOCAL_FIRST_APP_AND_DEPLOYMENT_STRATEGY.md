# Local-First App and Deployment Strategy

## 1. Executive summary

MIP's first product experience is **local-first**: users install the package, run a local command, open a browser workbench, provide data, run diagnostics and workflows, and view dashboards and reports on their machine. Hosted/team mode is a later optional extension.

This supports fast iteration, privacy-sensitive marketing data, and deterministic governance before cloud complexity.

## 2. Local-first strategy

```
User installs package
  → runs local command (e.g. mip demo / mip app)
  → local web server starts
  → browser opens
  → user uploads or points to data
  → MIP runs diagnostics / config / workflows
  → dashboards and reports served locally
  → user asks follow-up questions over artifacts
```

No requirement for cloud accounts, remote data upload, or autonomous production actions in initial releases.

## 3. Why local-first first

| Reason | Benefit |
|--------|---------|
| Data sensitivity | Marketing and revenue data stay on user machine |
| Iteration speed | Streamlit demo without multi-tenant infra |
| Governance testing | Gates, TrustReport, and tiers visible before scale |
| Engine integration | Path deps to local `mmm` and `panel_exp` siblings |
| LLM choice | Mock → Ollama → optional cloud without blocking demo |

## 4. Local app architecture

**Target shape:**

```
User browser
  → local dashboard / chat UI (Streamlit first)
  → local orchestration (workflows + llm packages)
  → MIP contracts / gates / evidence registry
  → MMM and GeoX adapters
  → LLM provider (Mock → Ollama → optional cloud)
  → local artifact store (run folders)
```

Packages (planned under `src/mip/`): `app/`, `dashboard/`, `reports/`, `workflows/`, `llm/`, `adapters/`.

## 5. LLM provider strategy

| Provider | When |
|----------|------|
| `MockLLMProvider` | Tests, Phase 1–6 deterministic demos |
| `LocalOllamaProvider` (or equivalent) | Private local demo with natural language |
| `CloudLLMProvider` | Optional; hosted/team mode |

**Rules:**

- Provider-agnostic interface in `mip.llm.providers`
- LLM receives **structured context** (TrustReport, contracts, lineage)—never raw engine internals only
- LLM cannot invent model outputs or change numeric contract fields
- Safety policies in `mip.llm.safety`

## 6. Dashboard/report hosting

- Dashboards run in local browser (Streamlit server on localhost)
- Reports export to **local files** under run folder
- **HTML first**, Markdown second, PDF later
- Display follows confidence-tier policy (see vision doc)

**Future concepts:** `DashboardViewPolicy`, `ReportSectionPolicy`, `ExportEligibility`.

| Tier | Display policy |
|------|----------------|
| decision_ready | Normal recommendation display |
| directional | Recommendations with warnings |
| diagnostic_only | Charts OK; production recommendation blocked |
| research_only | Watermark / research label |
| blocked | Show blockers; no decision recommendation |

## 7. Local artifact store

Suggested run folder layout:

```text
mip_runs/run_<timestamp>/
  input/           # uploaded data, manifests
  config/          # config drafts, validated configs
  diagnostics/     # readiness, feasibility reports
  artifacts/       # engine outputs, DecisionSurface, ExperimentEvidence
  reports/         # HTML, Markdown exports
  dashboard/       # serialized dashboard state
  trust/           # TrustReport snapshots
  lineage/         # WorkflowRun, RunManifest, provenance
```

**Artifact types may include:** data profile, `MMMConfigDraft`, `DataReadinessReport`, MMM/GeoX results, `DecisionSurface`, `ExperimentEvidence`, `CalibrationSignal`, `TrustReport`, HTML report, dashboard state, run manifest.

No remote persistence in Phase 5–7 unless user opts into hosted mode later.

## 8. Demo mode

**Demo mode** uses bundled or fixture artifacts when engines are not installed:

- Clearly labeled **demo fixtures** in UI and reports
- Same gate and TrustReport paths as production shapes
- No implication of decision-ready tier on synthetic data without disclosure

Command example: `mip demo --fixture saas_channel_roi`.

## 9. Production-grade local mode

Later local enhancements (still not hosted):

- Pin engine versions via Git deps
- Real MMM/GeoX adapter execution
- Ollama for explanations
- Stricter export gates and approval records
- Optional local SQLite for run index (not required initially)

## 10. Hosted/team mode

**Future optional mode** (Phase 11):

- FastAPI backend
- Persistent DB / object store for artifacts
- Authentication and team workspaces
- Scheduled workflows
- Cloud deployment (container or managed)
- Optional cloud LLM

Not immediate priority; local-first must remain fully functional without hosted dependencies.

## 11. Security/privacy considerations

- Local runs: data never leaves machine unless user exports or opts into cloud
- Secrets (API keys for optional cloud LLM) via env vars—not committed
- Run folders may contain sensitive data; document cleanup expectations
- Hosted mode requires authz, audit logs, and encryption at rest (TBD)

## 12. Non-goals

- Mandatory cloud signup for core features
- Uploading user data to MIP-operated servers in local-first mode
- Autonomous spend changes from local app
- PDF/report branding platform as decision authority without TrustReport

## 13. Phased implementation

| Phase | Deliverable |
|-------|-------------|
| 0 | This doc + vision + LLM roadmap |
| 5 | `mip demo` Streamlit shell + run folder creation |
| 6 | MMM dashboard panels + HTML report |
| 8 | Adapter-backed real artifacts in run folder |
| 10 | Approval + export eligibility |
| 11 | FastAPI + persistent hosted option |

## Related documents

- [LLM_DECISION_LAYER_VISION.md](./LLM_DECISION_LAYER_VISION.md)
- [LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md)

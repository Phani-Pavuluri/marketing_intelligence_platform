# Roadmap Execution Sequence

Condensed implementation sequence derived from [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md).

**Current main:** `1faf0cb`  
**Immediate next phase:** **P4** — Column mapping and semantic confirmation stubs (I6 / S1–S3)

## What is already implemented

| Layer | Status |
|-------|--------|
| P1 intake session + path recommendation (I1–I2) | ✓ |
| P2 required data assets + sample schemas (I3) | ✓ |
| P3 DataSourceRef + intake manifest (I5) | ✓ |
| Contracts, gates, TrustReport, evidence registry | ✓ |
| LLM Phase 1–5D (safety, intake, readiness, configs, orchestrator, CLI, MockLLM, Streamlit shell) | ✓ |
| Adapters 6A–6C, orchestration 7A–7C, static sibling bridge 8A–8F | ✓ |
| Roadmap docs: 8G–8N, P1–P13, S1–S12, G1–G20, I1–I15 | ✓ documented |

## Execution themes → roadmap tracks

| Theme | Tracks | Phase |
|-------|--------|-------|
| T1 Core semantics | S1–S12 | P4+ |
| T2 LLM-guided intake | I1–I3 | **P1–P2** |
| T3 Manifests | I4–I5, P8 | P3 |
| T4 Readiness | I6–I8 | P4–P5 |
| T5 CalibrationSignal | I9, P5 | P6 |
| T6 Lifecycle / current-state | P1, G11, G16 | P11 |
| T7 LLM answer governance | 8G–8N, G12–G20 | P12 |
| T8 Refresh governance | I12, P1, P5 | P10 |
| T9 Product UI | I10, I15, P11 | P7–P8 |
| T10 Golden scenarios | G1–G3, 8N | P13 |
| T11 Production hardening | I11, I13–I14, P9, P12 | P9 |
| T12 Live execution / optimizer | Phase 8+, P6–P7 | P15–P16 deferred |

## Dependency chain (summary)

```text
S1–S3 → I1–I3 → I5 manifest → I6 mapping → I7–I8 readiness → I12 refresh
  → 8F sibling export → P1/G11 lifecycle → 8G–8H → G1 golden → S6/G9 packet → P6–P7 → live (deferred)
```

## Implementation phases (P0–P16)

| Phase | Goal | Runtime allowed |
|-------|------|-----------------|
| **P0** | Roadmap audit ✓ | None |
| **P1** | I1–I2 intake session + path recommendation | Contracts/fixtures only | ✓ implemented |
| **P2** | I3 required data assets | Contracts/fixtures only | ✓ implemented |
| **P3** | I5 DataSourceRef + manifest | In-memory records | ✓ implemented |
| **P4** | I6 + S1–S3 semantic stubs | Validation on fixtures |
| **P5** | I7–I8 readiness reports | Demo file profiling |
| **P6** | I9 CalibrationSignal mapping | Fixture validation |
| **P7** | I10 Streamlit placeholders | Display only |
| **P8** | I4 demo upload profiling | Sandbox CSV only |
| **P9** | I11 production table-ref design | Design only |
| **P10** | I12 refresh governance | No model execution |
| **P11** | P1/G11/G16 lifecycle selection | Registry metadata |
| **P12** | 8G–8H LLM answer governance | MockLLM only |
| **P13** | G1–G3 golden harness | Fixture tests |
| **P14** | S6/G9 decision packet | Assembly only |
| **P15** | P6–P7 optimizer governance | **No optimizer execution** |
| **P16** | Live execution gate review | **Deferred** |

## Capability blockers (quick reference)

| Capability | Blocked until |
|------------|---------------|
| LLM current-performance answers | P11 + P12 + S1–S3 + TrustReport + G11–G20 |
| MMM refresh | P3, P5, P10, 8F handoff, G6 |
| Production data intake | P3, P5, P9, I13–I14, P9 audit |
| Budget recommendations | P14, P15, G15, G1, approval |
| Live engine execution | P13, P12, 8G–8N, G3, explicit signoff |

## Do not build yet

Model execution, optimizer execution, sibling imports, scheduled refresh, production connectors, external LLM providers, decision-ready budget actions, automatic artifact promotion.

## Canonical ownership (overlaps)

| Concept | Owner doc |
|---------|-----------|
| Metric/estimand/scope | Semantic S1–S3 |
| Current vs historical selection | Critical invariants G11, G16 |
| Upload/manifest workflow | Conversational intake I4–I5 |
| LLM safe answering | LLM reasoning 8G–8N + G12–G20 |
| Sibling handoff | Repo integration + 8F |
| Optimizer/budget | Platform completion P6–P7 + G15 |

## Related documents

- [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md) — full audit
- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](./PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
- [PLATFORM_COMPLETION_GAPS_ROADMAP.md](./PLATFORM_COMPLETION_GAPS_ROADMAP.md)

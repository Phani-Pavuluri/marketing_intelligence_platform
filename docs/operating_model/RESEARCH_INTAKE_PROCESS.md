# Research Intake Process

New methods, estimators, and orchestration patterns enter MIP through a structured intake process. Goal: reject unsafe shortcuts early and promote only what survives benchmarks and gates.

## Stages

### 1. Research intake

Submit a short charter: problem, proposed estimand, data requirements, and which engine(s) would own implementation. Assign an intake ID and reviewer.

**Deliverable:** Intake ticket with scope and non-goals (especially: no platform bidding).

### 2. Method summary

Precise definition of estimand, identification assumptions, and failure modes. Map to existing glossary terms or propose glossary additions via PR.

**Deliverable:** Method summary doc linked from intake ID.

### 3. Assumption mapping

Explicit list of assumptions (e.g., no interference, stable media mix, correct channel mapping). Tag which assumptions are testable with available diagnostics.

**Deliverable:** Assumption matrix with test hooks.

### 4. Prototype

Minimal implementation in a branch or sandbox package—not production engines. Prototype must emit draft contracts even if fields are partial.

**Deliverable:** Runnable prototype with example outputs.

### 5. Synthetic benchmark

Evaluate on synthetic world with known ground truth. Report bias, coverage, and runtime. Required for any new estimator claiming decision relevance.

**Deliverable:** Benchmark report with datasets referenced or generated in-repo.

### 6. Replay benchmark

Evaluate on frozen historical slices. Compare to incumbent method if any. Document regressions.

**Deliverable:** Replay report with versioned inputs.

### 7. Failure mode analysis

Structured review: when does the method lie confidently? Incompatible experiments, sparse data, collinearity, etc. Define blocked and downgraded tiers.

**Deliverable:** Failure mode doc tied to trust tier rules.

### 8. Production-readiness review

Checklist against [RELEASE_GATES.md](./RELEASE_GATES.md): contracts, tests, observability, documentation, orchestration boundaries if applicable.

**Deliverable:** Readiness checklist signed by reviewers.

### 9. Accept / reject / defer

| Outcome | Meaning |
|---------|---------|
| **Accept** | May proceed to engine integration and gate definition |
| **Reject** | Does not meet bar; registry note for audit |
| **Defer** | Promising but blocked on data, dependencies, or phase |

Accepted methods still require **per-artifact promotion** (e.g., each MMM version), not blanket approval.

## Roles (Initial)

- **Intake reviewer:** Science + platform representative
- **Engine owner:** Implements in correct `mip.*` package
- **Trust reviewer:** Tier and contract alignment

## Repository Conventions

- Research docs live under `docs/` or linked external spec; prototypes must not land fake logic in production engine paths without gates
- Intake ID referenced in ADRs when decisions change platform norms

See [EVALUATION_PHILOSOPHY.md](./EVALUATION_PHILOSOPHY.md).

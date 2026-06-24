# ADR-001: Full-Panel Δμ as MMM Production Decision Surface

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Platform architecture (initial constitution)

## Context

Media mix models produce multiple output types: channel curves, decomposition, attribution-style contributions, and counterfactual response surfaces. Teams often disagree on which view is “the number” for budget decisions. Using diagnostic views (e.g., decomposition shares) as commitment metrics leads to inconsistent planning, double counting, and poor alignment with optimization.

MIP must designate a **single production decision surface** for MMM-driven planning and optimization, while preserving other outputs for analysis and debugging.

## Decision

1. **Full-panel Δμ (delta-mu)**—the incremental outcome response over the full modeling panel for counterfactual spend changes—is the **only MMM output approved for production budget planning and optimization inputs**.
2. **Response curves, channel decomposition, and attribution-style breakdowns** are **diagnostic only**. They may inform hypotheses and model review but must not be promoted to `decision-ready` tier for allocation signing (per trust architecture).
3. Optimization engine inputs must reference a **promoted** MMM artifact that exposes a certified Δμ surface contract.
4. Orchestration and recommendations must label non-Δμ MMM views explicitly as diagnostic when surfaced to users.

## Consequences

### Positive

- Clear contract between MMM, optimization, and recommendations
- Reduces accidental use of non-causal or non-counterfactual summaries in solvers
- Simplifies release gates: promotion checks focus on Δμ quality and stability

### Negative

- Teams accustomed to decomposition-first workflows need migration and training
- Δμ surfaces require rigorous uncertainty and stability reporting before promotion
- Some stakeholder questions (“what % of sales is channel X?”) are answered only at diagnostic tier

### Operational

- `mip.mmm` implements Δμ as first-class artifact; diagnostics in separate contract types
- Documentation and glossary distinguish decision vs diagnostic estimands

## Alternatives Considered

| Alternative | Why not chosen |
|-------------|----------------|
| **Decomposition as decision metric** | Not a counterfactual estimand; confounded with base and correlated channels |
| **Multiple co-equal surfaces** | Invites inconsistent decisions and orchestration ambiguity |
| **Curve endpoints only** | Fragile to extrapolation; panel-integrated Δμ is more stable for planning grids |
| **No single surface (user picks)** | Shifts causal burden to consumers; violates contract-driven design |

## References

- [../glossary/ESTIMANDS.md](../glossary/ESTIMANDS.md)
- [../architecture/TRUST_ARCHITECTURE.md](../architecture/TRUST_ARCHITECTURE.md)

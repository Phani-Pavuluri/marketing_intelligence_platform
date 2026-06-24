# Estimands

Definitions for quantities MIP certifies or surfaces. Wording here is normative for contracts and documentation.

## estimand

The **target quantity** a method is designed to estimate, with explicit population, intervention, comparison, and outcome. Every engine output that supports decisions must declare its estimand. Ambiguous questions are resolved by estimand choice, not by narrative.

## lift

Relative change in outcome due to an intervention, typically \((Y_{\text{treated}} - Y_{\text{control}}) / Y_{\text{control}}\) or an experiment-defined variant. Lift is **design-dependent**; compare only across comparable designs and populations.

## incremental impact

Absolute change in outcome attributable to an intervention (e.g., additional conversions or revenue). Preferred for planning when budgets are in absolute currency or unit volumes. Must include uncertainty for decision-grade use.

## Δμ (delta-mu)

**Incremental outcome response** on the full MMM panel for a specified counterfactual change in media inputs—typically spend or exposure vectors. **Production decision estimand for MMM** per ADR-001. Reported over the panel that defines the planning problem, not a single channel in isolation.

## contribution

Share or level of outcome associated with a channel or factor in a **decomposition** of a model prediction. **Diagnostic estimand** in MIP: useful for understanding fit and storytelling, not for signing budget shifts without Δμ alignment.

## elasticity

Percent change in outcome per percent change in input (often spend or price). May be derived from Δμ surfaces locally. Tier depends on stability of the local linearization and uncertainty.

## calibration estimand

The quantity an **experiment** estimates that is used to adjust or constrain model parameters (e.g., incremental impact for a channel in a geo holdout). Must map to model structure via compatibility rules. Not identical to the planning Δμ unless mapping is certified.

## decision estimand

An estimand approved for **decision-ready** tier outputs after gates pass. In MMM planning, the primary decision estimand is **full-panel Δμ**. Incremental impact from promoted experiments may support calibration but is not a substitute for Δμ on the planning grid unless explicitly mapped in contracts.

## diagnostic vs decision-grade outputs

| Class | Purpose | Examples | Max tier (typical) |
|-------|---------|----------|-------------------|
| **Decision-grade** | Commitment, optimization input, signed scenarios | Full-panel Δμ; gated optimization allocation | `decision-ready` |
| **Diagnostic** | Model review, debugging, communication | Curves, decomposition, attribution views | `diagnostic only` |
| **Research** | Methods development | Prototype fits, synthetic benchmarks | `research only` |

Orchestration must not present diagnostic outputs with decision-grade language.

## Usage in Contracts (Future)

Contract fields will include: `estimand_id`, `population`, `intervention`, `comparison`, `outcome`, `time_horizon`, and `tier`. Implementation pending in `mip.contracts`.

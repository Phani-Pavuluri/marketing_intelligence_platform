# MMM LLM Response Template Rescoping 001

**Artifact ID:** `MIP_MMM_LLM_RESPONSE_TEMPLATE_RESCOPING_001`  
**Type:** design / rescoping only (not implementation)  
**Repo checkpoint:** `3c2e9c2` (MMM GeoX LLM layering reconciliation)  
**Status:** completed  
**Scope:** rescoping only — did not add or modify production code under `src/mip/`  
**Depends on:** `MIP_MMM_GEOX_LLM_LAYERING_RECONCILIATION_AUDIT_001` (`3c2e9c2`)

---

## 1. Purpose

Rescope the future MMM LLM response template so it consumes **`MMMResponseBoundaryApplicationOutput`**, not raw **`MMMLLMResponseBoundary`**.

The prior template audit (`MIP_MMM_LLM_RESPONSE_TEMPLATE_AUDIT_001`) scoped implementation to consume the boundary directly. Application packaging (`30d81a0`) now owns the JSON-safe application-facing payload. Implementing against the raw boundary would duplicate responsibilities.

This artifact does **not** implement the template, prompt execution, provider calls, or orchestration.

---

## 2. Decision

**`RESCOPE_TEMPLATE_TO_CONSUME_APPLICATION_PACKAGE_WITH_REFUSAL_ONLY_WHEN_NOT_READY`**

**Correct template input:** `MMMResponseBoundaryApplicationOutput`  
**Raw boundary direct input:** **not allowed**  
**Recommended next artifact:** `MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001`

### Handling of `ready_for_llm_prompt_assembly=false`

The application package currently **always** returns `ready_for_llm_prompt_assembly=false` (and the same for user-facing answer / full orchestration). That flag means **normal explanatory prompt assembly is blocked**.

Because the package still exposes `safe_response_guidance`, `cannot_say`, `unsupported_or_deferred_reasons`, `required_gates`, `blocked_capabilities`, provenance, and lineage, the future template **may** produce a **refusal-only / defer-only** instruction package. It must **not** assemble a normal rewrite/explain prompt that treats readiness as true.

**Refusal-only template when not ready:** **allowed**

---

## 3. Checkpoint presence

| Commit / artifact | Present? |
|-------------------|----------|
| `3c2e9c2` — layering reconciliation | **yes** |
| `30d81a0` — application package | **yes** |
| `a3edae9` — template readiness audit | **yes** |
| `4f7dbb7` — LLM response boundary | **yes** |

Confirmed chain:

```text
MMMPlanningRenderedResponse
→ MMMLLMResponseBoundary
→ MMMResponseBoundaryApplicationOutput
→ MMMLLMResponseTemplate   (future; not implemented)
```

---

## 4. Application package fields (evidence)

`MMMResponseBoundaryApplicationOutput` (`mip.llm.mmm_response_boundary_application`) exposes:

| Field | Present | Template consume? |
|-------|---------|-------------------|
| `application_status` | yes | **yes** — drives ready vs blocked vs refusal-only mode |
| `sections` (`section_id`, `title`, `rendered_text`, section-level can/cannot say, gates, deferred reasons, source refs) | yes | **yes** — section injection content |
| `can_say` | yes | **yes** — preserve; never expand beyond |
| `cannot_say` | yes | **yes** — preserve and **prioritize** over can_say |
| `unsupported_or_deferred_reasons` | yes | **yes** — must include / cannot omit |
| `safe_response_guidance` | yes | **yes** — system/developer guardrail text |
| `required_gates` | yes | **yes** — must include |
| `blocked_capabilities` | yes | **yes** — refusal framing |
| `provenance` | yes | **yes** — required for auditability |
| `lineage` | yes | **yes** — required for auditability |
| `ready_for_llm_prompt_assembly` | yes (always false today) | **yes** — blocks normal assembly |
| `ready_for_user_facing_answer` | yes (always false) | **yes** — keep false in template output metadata |
| `ready_for_full_orchestration` | yes (always false) | **yes** — keep false in template output metadata |

**Sufficiency:** Yes — enough for a metadata-only template that builds instruction slots and refusal-only packages without calling a provider.

---

## 5. What remains hidden behind the application package

The future template must **not** re-derive or re-read these from raw `MMMLLMResponseBoundary` unless the application package **explicitly** surfaces them with provenance:

| Lower-level boundary concern | Why hide |
|------------------------------|----------|
| `section_policies` / `MMMLLMSectionUsePolicy` | Boundary owns verbatim/rewrite policy; application already packages rendered text + can/cannot say |
| `refusal_policies` / per-refusal `forbidden_additions` enums | Application encodes safety via `safe_response_guidance` + `blocked_capabilities` + status; template must not invent parallel refusal catalogs from boundary |
| `must_include_sections` / `must_preserve_sections` / `may_rewrite_sections` / `cannot_omit_sections` | Application sections + dominance rules already define what may be shown |
| Raw `issues` / boundary status enums | Use `application_status` + unsupported/deferred reasons instead |
| Direct `build_mmm_llm_response_boundary(...)` calls inside the template builder | Would recreate the dual-consumer redundancy the reconciliation audit flagged |

`MMMLLMResponseBoundary` remains an **upstream** producer consumed by packaging — not a template input.

---

## 6. Instruction slots derived from the application package

Future `MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001` should define metadata-only slots (no provider execution):

1. **System slot** — from `safe_response_guidance` + `blocked_capabilities` + readiness flags (`ready_for_*=false`).  
2. **Developer / mode slot** — from `application_status`:  
   - if `ready_for_llm_prompt_assembly` is false → **refusal-only / defer-only mode**  
   - if blocked statuses → refuse/explain blockers only  
3. **Cannot-say slot** — `cannot_say` items as must-include / must-not-soften.  
4. **Can-say slot** — `can_say` items as may-paraphrase-lightly / forbidden-to-expand (only when not in refusal-only mode; when not ready, can_say is informational at most, not rewrite fodder).  
5. **Deferred / unsupported slot** — `unsupported_or_deferred_reasons` as cannot-omit.  
6. **Gates slot** — `required_gates` as cannot-omit / no bypass language.  
7. **Section injection slot** — `sections[].rendered_text` (and titles/ids) with section-level can/cannot say.  
8. **Provenance / lineage slot** — carry `provenance` + `lineage` into template metadata (not freeform LLM invention).

---

## 7. Rescoping questions answered

### 1. What fields does `MMMResponseBoundaryApplicationOutput` expose?

See §4.

### 2. Which fields should the future template consume?

All listed in §4 as “yes”, especially status, sections, can/cannot say, guidance, deferred reasons, gates, blocked capabilities, provenance, lineage, readiness flags.

### 3. Which lower-level boundary fields should remain hidden?

See §5 — section policies, refusal policies, forbidden-addition enums, include/preserve/rewrite lists, raw boundary builder.

### 4. Does the application package already include enough can_say / cannot_say / guidance / deferred / gates / provenance / lineage / readiness?

**Yes** for refusal-only and future constrained assembly. Normal assembly remains blocked by readiness flags today.

### 5. What instruction slots should be derived?

See §6.

### 6. What must the template not re-derive from the raw boundary?

Section policies, refusal catalogs, forbidden-addition enums, include/omit/rewrite lists — anything not exposed on the application package with provenance.

### 7. How should the template handle `ready_for_llm_prompt_assembly=false`?

Treat as **not ready for normal explanatory prompt assembly**. Emit refusal-only / defer-only instruction package when safe guidance exists; never flip readiness to true.

### 8. Block build entirely, or refusal-only?

**Refusal-only / defer-only allowed** when `safe_response_guidance` is present (it always is on the package). Do **not** hard-block the entire template builder — hard-block only **normal** prompt assembly.

### 9. Strict vs loose application boundary metadata?

- Prefer packages produced with `strict_boundary=True` (default).  
- If package status is `BLOCKED_BOUNDARY_VIOLATION` / missing can-say/cannot-say → refusal-only citing that block.  
- Loose / optional `response_boundary` mapping on input is an **upstream packaging concern**; the template only trusts what appears on the **output** with provenance.

### 10. Provenance requirements for optional loose `response_boundary` mapping?

Template must require:

- `provenance` present and non-empty enough to identify source (`source`, `strict_boundary`, section count at minimum)  
- `lineage` present with packaging artifact id / application name  
- If lineage indicates `response_boundary_present`, template may note that boundary metadata was packaged upstream — still **must not** open raw `MMMLLMResponseBoundary` objects  
- Missing provenance/lineage → refuse to build even refusal-only template (emit blocked template metadata / error status in the future implementation)

### 11. How to prevent `LLMExplanationPlan` from becoming a parallel MMM prompt path?

- MMM planning LLM template path is **only** `MMMResponseBoundaryApplicationOutput` → `MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001`.  
- `LLMExplanationRequest` / `LLMExplanationPlan` remain **generic adjacent** governed-explanation planning for other use cases.  
- Future MMM template code must not construct `LLMExplanationPlan` as a substitute for application-package instruction slots.  
- Docs/tests for the template implementation should assert no import/construction of `LLMExplanationPlan` as the MMM planning prompt path.

### 12. MMM-specific or generic?

**Still MMM-specific.** Generic response-boundary strategy remains deferred until this pattern is proven.

### 13. Is mypy cleanup required before implementation?

**No.** Global mypy failures are known pre-existing limitations (method-promotion consumer + application-package typing from `30d81a0`). They do not block metadata-only template implementation. Cleanup may proceed in parallel later.

### 14. Exact next implementation artifact?

**`MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001`**

---

## 8. Future implementation constraints

`MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001` must:

- consume `MMMResponseBoundaryApplicationOutput` only  
- **not** take `MMMLLMResponseBoundary` as direct input  
- treat `ready_for_llm_prompt_assembly=false` as blocking **normal** explanatory assembly  
- allow refusal-only / defer-only instruction packages when safe guidance exists  
- preserve `can_say`; prioritize `cannot_say`  
- preserve unsupported/deferred, gates, provenance, lineage, `safe_response_guidance`  
- create instruction slots from application package fields (§6)  
- avoid re-reading lower-level boundary policies without explicit package exposure + provenance  
- avoid `LLMExplanationPlan` parallel path  
- remain metadata-only (no provider call, no prompt execution, no orchestration)

Supersedes the prior next-artifact name `MIP_MMM_LLM_RESPONSE_TEMPLATE_001` where that meant “consume boundary directly.”

---

## 9. Gaps and risks

### Blocking gaps

None for proceeding to template implementation under the rescoped input.

### Redundancy risks

- Reintroducing a boundary-direct template consumer  
- Using `LLMExplanationPlan` as a parallel MMM planning prompt path  

### Compatibility risks

- Loose upstream `response_boundary` mapping without clear packaged provenance  
- Interpreting `ready_for_llm_prompt_assembly=false` as “build normal prompt anyway”  

### Known validation limitations

- Global `mypy src tests app` may fail on known pre-existing errors:  
  - 2 method-promotion handoff consumer typing errors  
  - 3 application-package typing errors from `30d81a0`  
- Not introduced by this rescope; not blocking next template implementation.

---

## 10. Boundary check (this artifact)

- No production contracts/workflows: **yes**  
- No template implementation: **yes**  
- No prompt/provider/orchestration: **yes**  
- No dataset generation: **yes**  
- No MMM/GeoX method logic: **yes**  
- No DecisionSurface/TrustReport/RecommendationContract: **yes**  
- No optimizer/simulator/spend/ROI/lift computation: **yes**  
- No method-promotion consumer changes: **yes**  
- No application-package behavior changes: **yes**  

---

## 11. Evidence paths

- `src/mip/llm/mmm_response_boundary_application.py`  
- `src/mip/contracts/mmm_llm_response_boundary.py`  
- `src/mip/workflows/mmm_llm_response_boundary.py`  
- `src/mip/contracts/llm_provider.py` (`LLMExplanationPlan`)  
- `docs/audits/MIP_MMM_GEOX_LLM_LAYERING_RECONCILIATION_AUDIT_001.md`  
- `docs/audits/MIP_MMM_LLM_RESPONSE_TEMPLATE_AUDIT_001.md`  
- `docs/contracts/MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001.md`  

# MIP Chat-First Demo UI UX Alignment Remediation 001

**Artifact ID:** `MIP_CHAT_FIRST_DEMO_UI_UX_ALIGNMENT_REMEDIATION_001`

## Outcome

The canonical Streamlit demo now opens as a chat-first MMM + GeoX measurement
copilot. The earlier implementation passed fixture, safety, and smoke tests but
presented the experience as a multi-tab governance dashboard: dropdown-led,
single-exchange, and dominated by technical detail. This remediation changes the
presentation layer while preserving the deterministic fixture backend and all
claim boundaries.

## Interaction model

The default landing view introduces the measurement copilot, sample-question
buttons, native Streamlit chat messages, a chat input, deterministic typed-question
matching, follow-up prompts, session history, and reset. Unsupported questions are
refused safely with guided prompts; no provider, prompt, embedding, or external
model path is used.

Primary responses are concise and user-facing: readiness, what is supported,
what remains blocked, and the next step appear first. Evidence, cannot-say text,
blocked claims, fixture lineage, and internal artifact names are progressively
disclosed in expanders. Compact readiness cards and an integrated lifecycle table
make the current stage visible without making the primary answer a dashboard.

## Legacy tools and boundaries

Cold-start advisory, readiness reports, calibration mapping, demo profiling, and
intake overview remain available under the secondary **Advanced tools** surface.
They are preserved but no longer dominate the landing page.

The demo remains fixture-backed and deterministic. ROI, ROAS, contribution,
budget recommendations, model-fit results, GeoX assignment, GeoX lift/readout,
and causal claims remain blocked. The Streamlit Cloud deployment contract remains
unchanged: `requirements.txt` retains `-e .` and the clean Docker deployment
regression remains authoritative.

## Files changed

- `app/streamlit_app.py`
- `src/mip/demo/chat_first_demo.py`
- `src/mip/demo/__init__.py`
- `tests/demo/test_chat_first_demo_ui_ux_alignment_001.py`
- this remediation record and summary JSON
- `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md`

## Local review and hosted status

Local startup and health checks passed, and deterministic interaction behavior is
covered by the scoped automated checks. Browser-driven visual review was not
available in this environment, so visual/manual acceptance remains pending the
formal manual-review result artifact. Hosted Streamlit verification also remains
pending after push.

## Recommended next artifact

`MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_001`

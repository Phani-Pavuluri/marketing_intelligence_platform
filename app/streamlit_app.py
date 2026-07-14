"""Canonical local/public deterministic Streamlit demo app (P7/P8).

Run::

    poetry run streamlit run app/streamlit_app.py

The app runs in deterministic mode by default. It does not require LLM providers,
API keys, FastAPI, Docker, or external services.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.demo_fixtures import (
    advisory_sample_labels,
    build_advisory_plan,
    build_calibration_fixture,
    build_demo_profiling_fixture,
    build_intake_overview_examples,
    build_readiness_reports,
    calibration_sample_labels,
    demo_profiling_fixture_labels,
    demo_profiling_links_advisory,
    demo_profiling_links_calibration,
    demo_profiling_links_readiness,
    readiness_sample_labels,
)
from app.ui_renderers import (
    BLOCKED_CLAIM_TOPICS,
    advisory_plan_to_display_dict,
    calibration_mapping_to_display_dict,
    demo_profile_to_display_dict,
    intake_recommendation_to_display_dict,
    mode_banner,
    readiness_report_to_display_dict,
)
from mip.demo.chat_first_demo import (
    ChatFirstDemoFixture,
    ChatResponseView,
    build_chat_response_view,
    build_prompt_widget_key,
    follow_up_questions,
    load_chat_first_demo_fixture,
    sample_prompt_labels,
)


def _render_mode_banner() -> None:
    banner = mode_banner()
    st.info(
        f"**Mode:** {banner['mode']}\n\n"
        f"{banner['description']}\n\n"
        "No LLM provider is configured or required. No external services are called."
    )


def _render_public_demo_safety() -> None:
    st.subheader("Public Demo Safety")
    st.markdown(
        """
This hosted demo is **deterministic-only**.

- It does **not** call LLM providers.
- It does **not** run MMM or GeoX engines.
- It does **not** estimate causal lift, ROI, power/MDE, matched markets,
  treatment/control assignment, or optimized budgets.
- It uses **synthetic demo fixtures** and governed summaries only.
- **No uploaded data is persisted.** This demo does not accept file uploads.
- Outputs are advisory, readiness, and mapping demonstrations—not production
  measurement decisions.
        """
    )


def _render_landing() -> None:
    st.title("Marketing Intelligence Platform — Public Demo")
    st.markdown(
        """
This app demonstrates governed intake, advisory planning, readiness, and
calibration mapping workflows using local synthetic demo fixtures.

- **Mode:** Deterministic — no LLM provider is configured or required.
- **No external services** are called.
- **No uploaded data** is persisted.
- It does **not** run MMM, GeoX, or LLM inference.
- It does **not** estimate lift, ROI, MDE, power, or optimized budgets.
- Outputs are deterministic MIP contracts and governed report objects.
        """
    )
    _render_public_demo_safety()


def _render_list(title: str, items: list[str]) -> None:
    st.subheader(title)
    if not items or items == ["None"]:
        st.write("None")
        return
    for item in items:
        st.write(f"- {item}")


def _render_blocked_claims() -> None:
    st.subheader("Blocked claim topics (deterministic guardrails)")
    for topic in BLOCKED_CLAIM_TOPICS:
        st.write(f"- {topic}")


def _render_chat_first_answer(response: ChatResponseView) -> None:
    """Render concise user-facing copy before governance detail."""
    st.caption("Deterministic answer")
    st.write(response.primary_answer)
    st.caption(response.readiness_label)
    st.warning(f"Blocked: {response.blocked_summary}")
    st.write(f"**Next step:** {response.next_step}")
    with st.expander("Why this answer"):
        st.write("This is a deterministic readiness explanation, not a model result.")
    with st.expander("Evidence inspected"):
        _render_list("Evidence inspected", list(response.evidence))
    with st.expander("What cannot be concluded"):
        _render_list("Cannot say", list(response.cannot_say))
        _render_list("Blocked claims", list(response.blocked_claims))
    with st.expander("Technical lineage"):
        st.write("Fixture readiness and allowed claims")
        st.write(f"Next required artifact: {response.technical_next_artifact or 'None'}")


def _render_chat_first_lifecycle(fixture: ChatFirstDemoFixture) -> None:
    st.subheader("Full MMM + GeoX lifecycle walkthrough")
    rows = [
        {
            "Stage": step.title,
            "Now": "Available" if step.available_now else "Blocked / future",
            "Status": step.status.replace("_", " "),
            "Next": "Evidence needed" if step.next_required_artifact else "Current context",
        }
        for step in fixture.lifecycle_steps
    ]
    st.dataframe(rows, hide_index=True, width="stretch")


def _initialize_chat_state() -> None:
    st.session_state.setdefault("chat_first_history", [])


def _submit_chat_prompt(fixture: ChatFirstDemoFixture, prompt: str) -> None:
    response = build_chat_response_view(fixture, prompt)
    st.session_state["chat_first_history"].extend(
        [{"role": "user", "content": prompt}, {"role": "assistant", "content": response}]
    )


def _render_readiness_cards(response: ChatResponseView) -> None:
    cards = (
        ("MMM", "Readiness available"),
        ("GeoX", "Design reviewable"),
        ("Data", "Compatibility checked"),
        ("Calibration", "Context only"),
        ("Recommendations", "Blocked"),
        ("Evidence", "Fixture-backed"),
    )
    st.subheader("Measurement status")
    for columns in (cards[:3], cards[3:]):
        for column, (label, status) in zip(st.columns(3), columns):
            column.caption(label)
            column.write(status)
    st.caption(f"Active answer: {response.readiness_label}")


def _render_chat_first_demo_tab() -> None:
    st.title("Marketing Intelligence Platform")
    st.subheader("MMM + GeoX measurement copilot")
    st.write(
        "Assess readiness, understand what the evidence supports, see what remains "
        "blocked, and choose the next measurement step."
    )
    st.caption("Deterministic demo — no model, provider, or external service is called.")

    try:
        fixture = load_chat_first_demo_fixture()
    except ValueError as exc:
        st.error(f"The demo fixture could not be loaded safely: {exc}")
        return

    _initialize_chat_state()
    history: list[dict[str, object]] = st.session_state["chat_first_history"]
    if st.button("Reset conversation", key="chat_first_reset"):
        st.session_state["chat_first_history"] = []
        st.rerun()
    if not history:
        with st.chat_message("assistant"):
            st.write("What would you like to understand about MMM, GeoX, or measurement readiness?")
        st.caption("Try a guided question")

    prompts = sample_prompt_labels(fixture)
    for index in range(0, len(prompts), 2):
        for position, (column, (label, question_id)) in enumerate(
            zip(st.columns(2), prompts[index : index + 2]),
            start=index,
        ):
            question = next(
                item.question for item in fixture.questions if item.question_id == question_id
            )
            if column.button(
                label,
                key=build_prompt_widget_key(
                    namespace="guided_prompt",
                    question_id=question_id,
                    position=position,
                ),
            ):
                _submit_chat_prompt(fixture, question)
                st.rerun()

    for message_index, entry in enumerate(history):
        with st.chat_message(str(entry["role"])):
            content = entry["content"]
            if isinstance(content, ChatResponseView):
                _render_chat_first_answer(content)
                follow_ups = follow_up_questions(fixture, content)
                if follow_ups:
                    st.caption("Suggested follow-ups")
                    for follow_up_position, item in enumerate(follow_ups):
                        key = build_prompt_widget_key(
                            namespace="conversation_follow_up",
                            question_id=item.question_id,
                            position=(message_index * 100) + follow_up_position,
                        )
                        if st.button(item.question, key=key):
                            _submit_chat_prompt(fixture, item.question)
                            st.rerun()
            else:
                st.write(str(content))

    typed_prompt = st.chat_input("Ask about readiness, evidence, MMM, GeoX, or planning")
    if typed_prompt:
        _submit_chat_prompt(fixture, typed_prompt)
        st.rerun()

    active_response = next(
        (
            entry["content"]
            for entry in reversed(history)
            if isinstance(entry["content"], ChatResponseView)
        ),
        build_chat_response_view(fixture, fixture.questions[0].question),
    )
    _render_readiness_cards(active_response)
    _render_chat_first_lifecycle(fixture)
    with st.expander("Fixture readiness and allowed claims"):
        _render_list("Allowed claims", list(fixture.allowed_claims))
        _render_list("Fixture-wide forbidden claims", list(fixture.forbidden_claims))


def _render_advisory_tab() -> None:
    st.header("Cold-start advisory")
    labels = advisory_sample_labels()
    sample_key = st.selectbox(
        "Select sample",
        options=list(labels.keys()),
        format_func=lambda key: labels[key],
        key="advisory_sample",
    )
    plan = build_advisory_plan(sample_key)
    display = advisory_plan_to_display_dict(plan)

    st.write(f"**Status:** {display['status_badge']} `{display['status']}`")
    st.write(f"**Evidence mode:** `{display['evidence_mode']}`")
    st.write(f"**Claim types:** {', '.join(f'`{c}`' for c in display['claim_types'])}")
    if display["evidence_levels"]:
        st.write(
            f"**Evidence levels:** {', '.join(f'`{e}`' for e in display['evidence_levels'])}"
        )

    st.warning(display["advisory_disclaimer"])

    st.subheader("Channel hypotheses")
    for hypothesis in display["channel_hypotheses"]:
        st.markdown(
            f"- **{hypothesis['channel']}** "
            f"(`{hypothesis['claim_type']}`, `{hypothesis['evidence_level']}`): "
            f"{hypothesis['summary']}"
        )
        if hypothesis["warnings"]:
            for warning in hypothesis["warnings"]:
                st.caption(f"  Warning: {warning}")

    st.subheader("Tracking checklist")
    st.write("Required items:")
    for item in display["tracking_checklist"]["required_items"]:
        st.write(f"- {item}")
    if display["tracking_checklist"]["missing_items"]:
        st.write("Missing items:")
        for item in display["tracking_checklist"]["missing_items"]:
            st.write(f"- {item}")

    with st.expander("Starter measurement plan"):
        st.json(display["measurement_plan"])

    with st.expander("Learning agenda"):
        st.json(display["learning_agenda"])

    _render_list("Warnings", display["warnings"])
    _render_list("Blocking reasons", display["blocking_reasons"])
    _render_list("Allowed next steps", display["allowed_next_steps"])
    _render_list("Blocked next steps", display["blocked_next_steps"])
    _render_blocked_claims()


def _render_readiness_tab() -> None:
    st.header("Workflow readiness reports")
    labels = readiness_sample_labels()
    sample_key = st.selectbox(
        "Select sample",
        options=list(labels.keys()),
        format_func=lambda key: labels[key],
        key="readiness_sample",
    )
    reports = build_readiness_reports(sample_key)

    for report in reports:
        display = readiness_report_to_display_dict(report)
        st.divider()
        st.subheader(display["report_type_label"])
        st.write(f"**Status:** {display['status_badge']} `{display['status']}`")

        route_keys = (
            "mmm_route",
            "geox_route",
            "calibration_route",
            "supported_route",
        )
        for route_key in route_keys:
            if route_key in display and display[route_key] is not None:
                st.write(f"**Route:** `{display[route_key]}`")

        finding_keys = [
            key
            for key in display
            if key.startswith("has_") or key.endswith("_ready") or key.endswith("_required")
        ]
        if finding_keys:
            with st.expander("Structural findings"):
                for key in sorted(finding_keys):
                    st.write(f"- `{key}`: `{display[key]}`")

        if display.get("required_next_inputs"):
            _render_list("Required next inputs", list(display["required_next_inputs"]))

        _render_list("Warnings", display["warnings"])
        _render_list("Blocking reasons", display["blocking_reasons"])
        _render_list("Allowed next steps", display["allowed_next_steps"])
        _render_list("Blocked next steps", display["blocked_next_steps"])

    _render_blocked_claims()


def _render_calibration_tab() -> None:
    st.header("CalibrationSignal intake mapping")
    labels = calibration_sample_labels()
    sample_key = st.selectbox(
        "Select sample",
        options=list(labels.keys()),
        format_func=lambda key: labels[key],
        key="calibration_sample",
    )
    result = build_calibration_fixture(sample_key)
    display = calibration_mapping_to_display_dict(
        result.report,
        signal_id=result.signal.calibration_id if result.signal is not None else None,
    )

    st.write(f"**Mapping status:** {display['status_badge']} `{display['status']}`")
    if display["mapped_signal_id"]:
        st.write(f"**Mapped signal ID:** `{display['mapped_signal_id']}`")
    else:
        st.write("**Mapped signal ID:** _not produced_")

    st.info(display["calibration_disclaimer"])

    _render_list("Missing fields", display["missing_fields"])
    _render_list("Incompatible fields", display["incompatible_fields"])
    _render_list("Warnings", display["warnings"])
    _render_list("Blocking reasons", display["blocking_reasons"])

    st.subheader("Source lineage")
    lineage: dict[str, Any] = display["lineage"]
    for key, value in lineage.items():
        st.write(f"- `{key}`: `{value}`")

    _render_list("Allowed next steps", display["allowed_next_steps"])
    _render_list("Blocked next steps", display["blocked_next_steps"])
    _render_blocked_claims()


def _render_demo_profiling_tab() -> None:
    st.header("Demo profiling")
    st.caption(
        "Safe local profiling over built-in synthetic tabular datasets. "
        "Summaries only — no raw rows stored, no file upload, no LLM calls."
    )
    labels = demo_profiling_fixture_labels()
    dataset_key = st.selectbox(
        "Select demo dataset",
        options=list(labels.keys()),
        format_func=lambda key: labels[key],
        key="demo_profiling_dataset",
    )
    fixture = build_demo_profiling_fixture(dataset_key)
    display = demo_profile_to_display_dict(fixture.profile, fixture.workflow_summary)

    st.write(f"**Dataset kind:** `{display['dataset_kind']}`")
    st.write(f"**Profile status:** {display['status_badge']} `{display['status']}`")
    st.write(f"**Rows / columns:** {display['row_count']} / {display['column_count']}")

    st.subheader("Coverage flags")
    flags = display["flags"]
    st.write(
        f"- Time: `{flags['has_time_data']}` · Geo: `{flags['has_geo_data']}` · "
        f"Media: `{flags['has_media_data']}` · Outcome: `{flags['has_outcome_data']}` · "
        f"Uncertainty: `{flags['has_uncertainty_data']}`"
    )
    st.write(f"**Time coverage:** {display['detected_time_coverage']}")
    st.write(f"**Geo coverage:** {display['detected_geo_coverage']}")
    _render_list("Detected sources", display["detected_sources"])
    _render_list("Detected channels", display["detected_channels"])
    _render_list("Detected metrics", display["detected_metrics"])
    _render_list("Warnings", display["warnings"])
    _render_list("Blocking reasons", display["blocking_reasons"])

    st.subheader("Columns and semantic roles")
    for column in display["columns"]:
        st.write(
            f"- `{column['column_name']}` → `{column['semantic_role']}` "
            f"({column['dtype_summary']}, distinct={column['distinct_count']})"
        )
        if column["sample_values"] != ["None"]:
            st.write(f"  - sample: {', '.join(column['sample_values'])}")

    st.subheader("Workflow link summary")
    st.write(f"**Common profile ID:** `{display['common_profile_summary_id'] or 'n/a'}`")
    st.write(f"**Traffic profile ID:** `{display['traffic_profile_id'] or 'n/a'}`")
    st.write(
        f"**Calibration evidence input ID:** "
        f"`{display['calibration_evidence_input_id'] or 'n/a'}`"
    )
    _render_list("Supported workflow routes", display["supported_routes"])
    _render_list("Blocked workflow routes", display["blocked_routes"])
    _render_list("Workflow warnings", display["workflow_warnings"])
    _render_list("Workflow blocking reasons", display["workflow_blocking_reasons"])

    st.subheader("Downstream workflow paths (deterministic)")
    if demo_profiling_links_advisory(dataset_key) and fixture.advisory_plan is not None:
        advisory_display = advisory_plan_to_display_dict(fixture.advisory_plan)
        st.write("**Cold-start advisory (data-informed):**")
        st.write(f"- Status: {advisory_display['status_badge']} `{advisory_display['status']}`")
        st.write(f"- Evidence mode: `{advisory_display['evidence_mode']}`")
    elif demo_profiling_links_advisory(dataset_key):
        st.write("Cold-start advisory: _not available for current profile status_")
    else:
        st.write("Cold-start advisory: _not applicable for this dataset kind_")

    if demo_profiling_links_readiness(dataset_key):
        st.write("**Readiness:** use supported/blocked routes above with common profile summary.")
        if fixture.common_summary is not None:
            st.write(f"- Common profile asset: `{fixture.common_summary.asset_type.value}`")
    else:
        st.write("Readiness route hints: _see workflow routes above_")

    if demo_profiling_links_calibration(dataset_key):
        if fixture.calibration_report is not None:
            cal_display = calibration_mapping_to_display_dict(fixture.calibration_report)
            st.write("**Calibration mapping:**")
            st.write(f"- Status: {cal_display['status_badge']} `{cal_display['status']}`")
            _render_list("Blocking reasons", cal_display["blocking_reasons"])
        else:
            st.write("Calibration mapping: _evidence input not produced_")
    else:
        st.write("Calibration mapping: _not applicable for this dataset kind_")


def _render_intake_overview_tab() -> None:
    st.header("Intake overview")
    st.caption("Deterministic intake path recommendation examples.")
    for example in build_intake_overview_examples():
        display = intake_recommendation_to_display_dict(
            example.label,
            example.recommendation,
            example.session,
        )
        st.divider()
        st.subheader(display["label"])
        st.write(f"**Business question:** {display['business_question']}")
        st.write(f"**Workflow kind:** `{display['workflow_kind']}`")
        st.write(f"**Recommended path:** `{display['recommended_path']}`")
        st.write(f"**Status:** {display['status_badge']}")
        st.write(display["why_this_path"])
        _render_list("Why other paths blocked", display["why_other_paths_blocked"])
        _render_list("Warnings", display["warnings"])
        _render_list("Blocking reasons", display["blocking_reasons"])
        _render_list("Allowed next steps", display["allowed_next_steps"])
        _render_list("Blocked next steps", display["blocked_next_steps"])


def main() -> None:
    """Streamlit entrypoint for the deterministic measurement copilot demo."""
    st.set_page_config(
        page_title="MIP Measurement Copilot",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    with st.sidebar:
        st.header("MIP demo")
        surface = st.radio(
            "Workspace",
            ("Measurement copilot", "Advanced tools"),
            label_visibility="collapsed",
        )
        st.caption("Deterministic fixture-backed demo")

    if surface == "Measurement copilot":
        _render_chat_first_demo_tab()
        return

    st.title("Advanced tools")
    st.caption("Legacy deterministic tools remain available for detailed inspection.")
    legacy_tool = st.selectbox(
        "Choose a legacy tool",
        (
            "Cold-start advisory",
            "Readiness reports",
            "Calibration mapping",
            "Demo profiling",
            "Intake overview",
        ),
    )
    if legacy_tool == "Cold-start advisory":
        _render_advisory_tab()
    elif legacy_tool == "Readiness reports":
        _render_readiness_tab()
    elif legacy_tool == "Calibration mapping":
        _render_calibration_tab()
    elif legacy_tool == "Demo profiling":
        _render_demo_profiling_tab()
    else:
        _render_intake_overview_tab()


if __name__ == "__main__":
    main()

"""P7 local deterministic workflow UI shell (Streamlit)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.demo_fixtures import (
    advisory_sample_labels,
    build_advisory_plan,
    build_calibration_fixture,
    build_intake_overview_examples,
    build_readiness_reports,
    calibration_sample_labels,
    readiness_sample_labels,
)
from app.ui_renderers import (
    BLOCKED_CLAIM_TOPICS,
    advisory_plan_to_display_dict,
    calibration_mapping_to_display_dict,
    intake_recommendation_to_display_dict,
    mode_banner,
    readiness_report_to_display_dict,
)


def _render_mode_banner() -> None:
    banner = mode_banner()
    st.info(f"**Mode:** {banner['mode']}\n\n{banner['description']}")


def _render_landing() -> None:
    st.title("Marketing Intelligence Platform — Local Demo Shell")
    st.markdown(
        """
This local app demonstrates governed intake, advisory planning, readiness, and
calibration mapping workflows.

- It does **not** run MMM, GeoX, or LLM inference.
- It does **not** estimate lift, ROI, MDE, power, or optimized budgets.
- Outputs are deterministic MIP contracts and governed report objects.
        """
    )


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
    """Streamlit entrypoint for the P7 local deterministic workflow shell."""
    st.set_page_config(
        page_title="MIP Local Demo Shell",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _render_mode_banner()
    _render_landing()

    tab_advisory, tab_readiness, tab_calibration, tab_intake = st.tabs(
        [
            "Cold-start advisory",
            "Readiness reports",
            "Calibration mapping",
            "Intake overview",
        ]
    )

    with tab_advisory:
        _render_advisory_tab()
    with tab_readiness:
        _render_readiness_tab()
    with tab_calibration:
        _render_calibration_tab()
    with tab_intake:
        _render_intake_overview_tab()


if __name__ == "__main__":
    main()

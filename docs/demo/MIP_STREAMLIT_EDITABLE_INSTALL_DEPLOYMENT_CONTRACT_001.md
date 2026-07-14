# MIP Streamlit Editable Install Deployment Contract 001

**Artifact ID:** `MIP_STREAMLIT_EDITABLE_INSTALL_DEPLOYMENT_CONTRACT_001`
**Type:** deployment contract
**Verdict:** `KEEP_EDITABLE_MARKER_AND_UPDATE_CONTRACT`

## Purpose

This artifact records the current packaging contract for the canonical public
Streamlit demo at `app/streamlit_app.py`. It reconciles the earlier P9 readiness
test, which incorrectly expected a bare `.` requirement, with the intentional
`fa504b9` change to `-e .` in `requirements.txt`.

## Current contract

Streamlit Community Cloud installs `requirements.txt` from the checked-out
repository. The local MIP package requirement must be `-e .`. This is a real
editable package installation, not a `sys.path` workaround: it resolves
`src/mip` against the repository checkout while preserving access to files that
remain at repository level.

The chat-first fixture loader uses
`data/demo/domain_fixtures/saas_subscriptions/v1`. A non-editable built wheel
can import `mip`, but the current wheel does not include those repository-level
`data/demo/...` assets. Replacing `-e .` with `.` therefore breaks clean
requirements-only loading of `saas_subscriptions_demo_v1`.

## Verification

`make validate-public-deployment` runs a fresh Python 3.11 Docker container. It
installs only `requirements.txt`, imports `mip.demo.chat_first_demo` and the
canonical `app.streamlit_app`, then loads `saas_subscriptions_demo_v1` through
the real fixture loader. It uses no Poetry or host fallback.

Local Streamlit and the public Streamlit entrypoint were manually confirmed to
load. UI alignment remains a separate task; this contract changes neither UI
behavior nor model, provider, MMM, GeoX, ROI, or recommendation behavior.

## Future packaging option

Moving fixture assets into package resources could permit a future non-editable
wheel contract. That would require a separate packaging implementation, a
resource-loading change, and a replacement deployment validation contract. It
is out of scope here.

## Recommended next artifact

`MIP_CHAT_FIRST_DEMO_UI_UX_ALIGNMENT_REMEDIATION_001`

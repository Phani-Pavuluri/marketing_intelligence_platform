"""Tests for public mip.workflows.configs exports."""


def test_public_imports() -> None:
    from mip.workflows.configs import (
        PRE_PERIOD_PLACEHOLDER,
        ConfigDraftMetadata,
        ConfigDraftValidationReport,
        DraftConfigStatus,
        GeoXConfigDraft,
        MMMConfigDraft,
        draft_config_for_objective,
        draft_geox_config,
        draft_mmm_config,
    )

    assert DraftConfigStatus.DRAFTABLE.value == "draftable"
    assert PRE_PERIOD_PLACEHOLDER == "TBD: pre_period"
    assert callable(draft_mmm_config)
    assert callable(draft_geox_config)
    assert callable(draft_config_for_objective)
    assert MMMConfigDraft is not None
    assert GeoXConfigDraft is not None
    assert ConfigDraftMetadata is not None
    assert ConfigDraftValidationReport is not None

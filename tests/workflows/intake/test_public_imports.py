"""Tests for public mip.workflows.intake exports."""


def test_public_imports() -> None:
    from mip.workflows.intake import (
        BusinessObjective,
        BusinessObjectiveType,
        ColumnMappingProposal,
        ColumnMappingStatus,
        DataAvailabilityProfile,
        DataFieldRequirement,
        DataFieldRole,
        DataGrain,
        DataSourceMode,
        DataSourceRef,
        DecisionHorizon,
        DecisionScope,
        FeasibilityStatus,
        GeoGrain,
        GeoXIntakeManifest,
        GeoXIntakeSession,
        IntakeCandidatePath,
        IntakeIntendedUse,
        IntakePathRecommendation,
        IntakePlan,
        IntakeRecommendationStatus,
        IntakeSessionStatus,
        MeasurementIntakeSession,
        MeasurementWorkflowKind,
        MMMIntakeManifest,
        MMMIntakeSession,
        ObjectiveDataRequirement,
        ObjectiveFeasibilityReport,
        RiskTolerance,
        SemanticMappingDimension,
        SemanticMappingReport,
        WorkflowType,
        build_intake_manifest,
        build_intake_plan,
        build_semantic_mapping_report,
        evaluate_objective_feasibility,
        has_field_or_alias,
        recommend_intake_path,
        recommended_next_questions,
        requirement_for_objective,
    )

    assert MeasurementWorkflowKind.MMM.value == "mmm"
    assert IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM.value == "national_diagnostic_mmm"
    assert DataGrain.WEEKLY.value == "weekly"
    assert GeoGrain.NATIONAL.value == "national"
    assert IntakeSessionStatus.DRAFT.value == "draft"
    assert IntakeRecommendationStatus.RECOMMENDED.value == "recommended"
    assert IntakeIntendedUse.DIAGNOSTIC_ONLY.value == "diagnostic_only"
    assert callable(recommend_intake_path)
    assert callable(build_intake_plan)
    assert callable(build_intake_manifest)
    assert callable(build_semantic_mapping_report)
    assert SemanticMappingReport is not None
    assert ColumnMappingProposal is not None
    assert ColumnMappingStatus.PROPOSED.value == "proposed"
    assert SemanticMappingDimension.DATE.value == "date"
    assert IntakePlan is not None
    assert MMMIntakeManifest is not None
    assert GeoXIntakeManifest is not None
    assert DataSourceRef is not None
    assert DataSourceMode.STREAMLIT_FILE_UPLOAD.value == "streamlit_file_upload"
    assert MeasurementIntakeSession is not None
    assert MMMIntakeSession is not None
    assert GeoXIntakeSession is not None
    assert IntakePathRecommendation is not None

    assert BusinessObjectiveType.CONVERSION_ROI.value == "conversion_roi"
    assert WorkflowType.MMM_CHANNEL_ROI.value == "mmm_channel_roi"
    assert DataFieldRole.REQUIRED.value == "required"
    assert FeasibilityStatus.FEASIBLE.value == "feasible"
    assert DecisionHorizon.UNKNOWN.value == "unknown"
    assert DecisionScope.CHANNEL.value == "channel"
    assert RiskTolerance.BALANCED.value == "balanced"
    assert callable(requirement_for_objective)
    assert callable(evaluate_objective_feasibility)
    assert callable(recommended_next_questions)
    assert callable(has_field_or_alias)
    assert BusinessObjective is not None
    assert DataAvailabilityProfile is not None
    assert DataFieldRequirement is not None
    assert ObjectiveDataRequirement is not None
    assert ObjectiveFeasibilityReport is not None

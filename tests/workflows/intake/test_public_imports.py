"""Tests for public mip.workflows.intake exports."""


def test_public_imports() -> None:
    from mip.workflows.intake import (
        BusinessObjective,
        BusinessObjectiveType,
        ColumnMappingProposal,
        ColumnMappingStatus,
        CommonDataProfileSummary,
        CommonIntakeStatus,
        CommonIntakeWorkbench,
        DataAvailabilityProfile,
        DataFieldRequirement,
        DataFieldRole,
        DataGrain,
        DataSourceMode,
        DataSourceRef,
        DecisionHorizon,
        DecisionScope,
        ExperimentDesignEntryPath,
        ExperimentDesignIntake,
        ExperimentDesignStatus,
        ExperimentDiagnosticRequest,
        ExperimentKpiFamily,
        ExperimentObjectiveCategory,
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
        MMMToGeoXDesignBridge,
        ObjectiveDataRequirement,
        ObjectiveFeasibilityReport,
        RiskTolerance,
        SemanticMappingDimension,
        SemanticMappingReport,
        StandaloneGeoXDesignRequest,
        WorkflowSupportAssessment,
        WorkflowSupportRoute,
        WorkflowSupportStatus,
        WorkflowType,
        build_common_intake_workbench,
        build_experiment_design_intake,
        build_experiment_diagnostic_request,
        build_intake_manifest,
        build_intake_plan,
        build_llm_answer_grounding_context,
        build_semantic_mapping_report,
        build_workflow_support_assessment,
        evaluate_objective_feasibility,
        has_field_or_alias,
        recommend_intake_path,
        recommended_next_questions,
        requirement_for_objective,
        suggest_kpi_families_for_objective,
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
    assert callable(build_workflow_support_assessment)
    assert callable(build_common_intake_workbench)
    assert callable(build_llm_answer_grounding_context)
    assert CommonIntakeWorkbench is not None
    assert WorkflowSupportRoute.NATIONAL_MMM.value == "national_mmm"
    assert WorkflowSupportStatus.SUPPORTED.value == "supported"
    assert CommonIntakeStatus.SUPPORT_ASSESSED.value == "support_assessed"
    assert WorkflowSupportAssessment is not None
    assert CommonDataProfileSummary is not None
    assert callable(build_experiment_design_intake)
    assert callable(build_experiment_diagnostic_request)
    assert callable(suggest_kpi_families_for_objective)
    assert ExperimentDesignEntryPath.MMM_DRIVEN.value == "mmm_driven"
    assert ExperimentObjectiveCategory.AWARENESS.value == "awareness"
    assert ExperimentKpiFamily.AWARENESS_SEARCH.value == "awareness_search"
    assert ExperimentDesignStatus.REQUIREMENTS_READY.value == "requirements_ready"
    assert MMMToGeoXDesignBridge is not None
    assert StandaloneGeoXDesignRequest is not None
    assert ExperimentDesignIntake is not None
    assert ExperimentDiagnosticRequest is not None
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

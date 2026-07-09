"""GeoX readout fixture materialization workflow (narrow local fixtures only)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]

from mip.contracts.geox_fixture_materialization import (
    GeoXFixtureDatasetMaterializationRequest,
    GeoXFixtureMaterializationIssueCode,
    GeoXFixtureMaterializationPolicy,
    GeoXFixtureMaterializationRequest,
    GeoXFixtureMaterializationResult,
    GeoXFixtureMaterializationStatus,
    GeoXMaterializedDataset,
    GeoXMaterializedDatasetRole,
)
from mip.contracts.geox_panel_exp_integration import GeoXMaterializedInputAvailability
from mip.contracts.geox_readout_input_resolution import DatasetReference, DatasetSourceType


def materialize_geox_readout_fixtures(
    request: GeoXFixtureMaterializationRequest,
) -> GeoXFixtureMaterializationResult:
    """Materialize multiple fixture datasets under policy constraints."""
    if not request.policy.enabled:
        return _blocked_result(
            request.request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_MATERIALIZATION_DISABLED,
            [GeoXFixtureMaterializationIssueCode.MATERIALIZATION_DISABLED],
            request,
        )

    materialized: list[GeoXMaterializedDataset] = []
    issues: list[GeoXFixtureMaterializationIssueCode] = []
    warnings = list(request.warnings)
    status = GeoXFixtureMaterializationStatus.MATERIALIZED
    spend_dataset: GeoXMaterializedDataset | None = None
    assignment_dataset: GeoXMaterializedDataset | None = None

    for dataset_request in request.dataset_requests:
        single = materialize_geox_fixture_dataset(
            dataset_request,
            policy=request.policy,
        )
        warnings.extend(single.warnings)
        issues.extend(single.issues)
        if single.status != GeoXFixtureMaterializationStatus.MATERIALIZED:
            status = single.status
            continue
        if single.materialized_datasets:
            dataset = single.materialized_datasets[0]
            materialized.append(dataset)
            if dataset.role == GeoXMaterializedDatasetRole.SPEND:
                spend_dataset = dataset
            elif dataset.role == GeoXMaterializedDatasetRole.ASSIGNMENT:
                assignment_dataset = dataset

    roles_requested = {item.role for item in request.dataset_requests}
    if (
        status == GeoXFixtureMaterializationStatus.MATERIALIZED
        and GeoXMaterializedDatasetRole.SPEND in roles_requested
        and spend_dataset is None
    ):
        status = GeoXFixtureMaterializationStatus.BLOCKED_SPEND_DATASET_MISSING
        issues.append(GeoXFixtureMaterializationIssueCode.SPEND_DATASET_MISSING)
    if (
        status == GeoXFixtureMaterializationStatus.MATERIALIZED
        and GeoXMaterializedDatasetRole.ASSIGNMENT in roles_requested
        and assignment_dataset is None
    ):
        status = GeoXFixtureMaterializationStatus.BLOCKED_ASSIGNMENT_DATASET_MISSING
        issues.append(GeoXFixtureMaterializationIssueCode.ASSIGNMENT_DATASET_MISSING)

    issues.extend(
        [
            GeoXFixtureMaterializationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED,
            GeoXFixtureMaterializationIssueCode.POST_TEST_SPEND_INPUT_NOT_INSTANTIATED,
        ]
    )

    return GeoXFixtureMaterializationResult(
        request_id=request.request_id,
        status=status,
        materialized_datasets=materialized,
        spend_dataset=spend_dataset,
        assignment_dataset=assignment_dataset,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={
            **request.lineage,
            **request.policy.lineage,
            "materialization_mode": "fixture_local_only",
        },
    )


def materialize_geox_fixture_dataset(
    request: GeoXFixtureDatasetMaterializationRequest,
    *,
    policy: GeoXFixtureMaterializationPolicy | None = None,
) -> GeoXFixtureMaterializationResult:
    """Materialize one dataset reference from a controlled local fixture."""
    active_policy = policy or GeoXFixtureMaterializationPolicy()
    request_id = request.dataset_ref.dataset_ref_id

    if not active_policy.enabled:
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_MATERIALIZATION_DISABLED,
            [GeoXFixtureMaterializationIssueCode.MATERIALIZATION_DISABLED],
            warnings=request.warnings,
        )

    if request.role == GeoXMaterializedDatasetRole.UNKNOWN:
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_DATASET_ROLE_UNCLEAR,
            [GeoXFixtureMaterializationIssueCode.DATASET_ROLE_UNCLEAR],
            warnings=request.warnings,
        )

    ref = request.dataset_ref
    if ref.source_type not in active_policy.allowed_source_types:
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_SOURCE_TYPE_UNSUPPORTED,
            [
                GeoXFixtureMaterializationIssueCode.SOURCE_TYPE_UNSUPPORTED_FOR_FIXTURE_MATERIALIZATION
            ],
            warnings=request.warnings,
        )

    if (
        ref.source_type == DatasetSourceType.REGISTERED_ARTIFACT
        and not ref.source_uri_or_handle.strip()
    ):
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_SOURCE_NOT_REGISTERED,
            [GeoXFixtureMaterializationIssueCode.SOURCE_NOT_REGISTERED],
            warnings=request.warnings,
        )

    try:
        fixture_path = _resolve_fixture_path(ref, active_policy)
    except _PathNotAllowed:
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_LOCAL_PATH_NOT_ALLOWED,
            [GeoXFixtureMaterializationIssueCode.LOCAL_PATH_OUTSIDE_ALLOWED_FIXTURE_ROOT],
            warnings=request.warnings,
        )
    except _FileNotFound:
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_LOCAL_FILE_NOT_FOUND,
            [GeoXFixtureMaterializationIssueCode.LOCAL_FILE_NOT_FOUND],
            warnings=request.warnings,
        )

    if fixture_path.suffix.lower() not in {
        extension.lower() for extension in active_policy.allowed_file_extensions
    }:
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_FILE_FORMAT_UNSUPPORTED,
            [GeoXFixtureMaterializationIssueCode.FILE_FORMAT_UNSUPPORTED],
            warnings=request.warnings,
        )

    dataframe = pd.read_csv(fixture_path)
    if len(dataframe) > active_policy.max_rows:
        dataframe = dataframe.head(active_policy.max_rows)
        warnings = list(request.warnings) + [
            f"Fixture truncated to policy max_rows={active_policy.max_rows}"
        ]
    else:
        warnings = list(request.warnings)

    columns = [str(column) for column in dataframe.columns]
    missing = [column for column in request.required_columns if column not in columns]
    if missing:
        return _blocked_result(
            request_id,
            GeoXFixtureMaterializationStatus.BLOCKED_DECLARED_COLUMNS_MISSING,
            [GeoXFixtureMaterializationIssueCode.DECLARED_COLUMNS_MISSING_FROM_MATERIALIZED_DATA],
            warnings=warnings,
            extra_issues_missing=missing,
        )

    materialized = GeoXMaterializedDataset(
        dataset_ref_id=ref.dataset_ref_id,
        role=request.role,
        dataframe=dataframe,
        columns=columns,
        row_count=len(dataframe),
        source_lineage={
            "dataset_ref_id": ref.dataset_ref_id,
            "source_type": str(ref.source_type),
            "fixture_path": str(fixture_path),
            "row_count": str(len(dataframe)),
            "columns": ",".join(columns),
            **request.lineage,
        },
        warnings=warnings,
    )

    return GeoXFixtureMaterializationResult(
        request_id=request_id,
        status=GeoXFixtureMaterializationStatus.MATERIALIZED,
        materialized_datasets=[materialized],
        spend_dataset=materialized if request.role == GeoXMaterializedDatasetRole.SPEND else None,
        assignment_dataset=(
            materialized if request.role == GeoXMaterializedDatasetRole.ASSIGNMENT else None
        ),
        issues=[
            GeoXFixtureMaterializationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED,
            GeoXFixtureMaterializationIssueCode.POST_TEST_SPEND_INPUT_NOT_INSTANTIATED,
        ],
        warnings=warnings,
        lineage={"fixture_path": str(fixture_path)},
    )


def build_materialized_input_availability_from_fixture_result(
    result: GeoXFixtureMaterializationResult,
) -> GeoXMaterializedInputAvailability:
    """Map fixture materialization output to Stage 3A availability indicators only."""
    spend_ref = (
        result.spend_dataset.source_lineage.get("fixture_path")
        if result.spend_dataset is not None
        else None
    )
    assignment_ref = (
        result.assignment_dataset.source_lineage.get("fixture_path")
        if result.assignment_dataset is not None
        else None
    )
    return GeoXMaterializedInputAvailability(
        has_materialized_spend_df=result.spend_dataset is not None,
        has_materialized_assignment_df=result.assignment_dataset is not None,
        has_assignment_mapping=result.assignment_dataset is not None,
        materialized_spend_ref_optional=spend_ref,
        materialized_assignment_ref_optional=assignment_ref,
        lineage={
            **result.lineage,
            "materialization_status": str(result.status),
            "materialized_dataset_count": str(len(result.materialized_datasets)),
        },
        warnings=list(result.warnings),
    )


class _PathNotAllowed(Exception):
    pass


class _FileNotFound(Exception):
    pass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_fixture_path(
    ref: DatasetReference,
    policy: GeoXFixtureMaterializationPolicy,
) -> Path:
    relative_path = _fixture_relative_path(ref)
    if ".." in Path(relative_path).parts:
        raise _PathNotAllowed

    repo_root = _repo_root()
    candidate = (repo_root / relative_path).resolve()
    for root in policy.allowed_fixture_roots:
        allowed_root = (repo_root / root).resolve()
        try:
            candidate.relative_to(allowed_root)
            if candidate.is_file():
                return candidate
            raise _FileNotFound
        except ValueError:
            continue
    raise _PathNotAllowed


def _fixture_relative_path(ref: DatasetReference) -> str:
    handle = ref.source_uri_or_handle.strip()
    if handle.startswith("fixture://"):
        return handle.removeprefix("fixture://")
    if handle.startswith("registered://"):
        return handle.removeprefix("registered://")
    if ref.file_name_or_table_name.strip():
        return ref.file_name_or_table_name.strip()
    return handle


def _blocked_result(
    request_id: str,
    status: GeoXFixtureMaterializationStatus,
    issues: list[GeoXFixtureMaterializationIssueCode],
    request: GeoXFixtureMaterializationRequest | None = None,
    *,
    warnings: list[str] | None = None,
    extra_issues_missing: list[str] | None = None,
) -> GeoXFixtureMaterializationResult:
    merged_warnings = list(warnings or [])
    if request is not None:
        merged_warnings = list(dict.fromkeys(request.warnings + merged_warnings))
    if extra_issues_missing:
        merged_warnings.append(f"Missing required columns: {', '.join(extra_issues_missing)}")
    all_issues = list(issues)
    all_issues.extend(
        [
            GeoXFixtureMaterializationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED,
            GeoXFixtureMaterializationIssueCode.POST_TEST_SPEND_INPUT_NOT_INSTANTIATED,
        ]
    )
    lineage = request.lineage if request is not None else {}
    return GeoXFixtureMaterializationResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(all_issues),
        warnings=merged_warnings,
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXFixtureMaterializationIssueCode],
) -> list[GeoXFixtureMaterializationIssueCode]:
    seen: set[GeoXFixtureMaterializationIssueCode] = set()
    ordered: list[GeoXFixtureMaterializationIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered

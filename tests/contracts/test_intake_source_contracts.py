"""Tests for intake data source reference contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts.intake import DataGrain, GeoGrain
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceRef,
    DataSourceStatus,
    DataSourceType,
    DropzoneSourceRef,
    FileSourceRef,
    SiblingExportSourceRef,
    TableSourceRef,
    UploadedFileSourceRef,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _base_source_kwargs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "source_id": "src-001",
        "asset_type": DataAssetType.OUTCOME_KPI_DATA,
        "uri_or_table_ref": "sandbox://demo/outcome.csv",
        "created_at": _NOW,
    }
    base.update(overrides)
    return base


def test_table_source_ref_construction() -> None:
    source = TableSourceRef(
        **_base_source_kwargs(
            source_mode=DataSourceMode.GOVERNED_TABLE_REFERENCE,
            source_type=DataSourceType.TABLE,
            uri_or_table_ref="catalog.schema.outcome_kpi",
        )
    )
    assert source.source_mode == "governed_table_reference"
    assert source.read_only is True


def test_file_source_ref_construction() -> None:
    source = FileSourceRef(
        **_base_source_kwargs(
            source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
            source_type=DataSourceType.FILE,
            uri_or_table_ref="/data/intake/media.csv",
        )
    )
    assert source.source_type == "file"


def test_uploaded_file_source_ref_construction() -> None:
    source = UploadedFileSourceRef(
        **_base_source_kwargs(
            source_mode=DataSourceMode.STREAMLIT_FILE_UPLOAD,
            source_type=DataSourceType.FILE,
            uri_or_table_ref="upload://session/outcome.csv",
        )
    )
    assert source.source_mode == "streamlit_file_upload"


def test_dropzone_source_ref_construction() -> None:
    source = DropzoneSourceRef(
        **_base_source_kwargs(
            source_mode=DataSourceMode.LOCAL_DROPZONE_FOLDER,
            source_type=DataSourceType.FOLDER,
            uri_or_table_ref="/dropzone/intake-session-001",
        )
    )
    assert source.source_type == "folder"


def test_sibling_export_source_ref_construction() -> None:
    source = SiblingExportSourceRef(
        **_base_source_kwargs(
            source_mode=DataSourceMode.SIBLING_REPO_STATIC_EXPORT,
            source_type=DataSourceType.SIBLING_EXPORT,
            uri_or_table_ref="sibling://mmm/fixtures/export_v1.json",
            asset_type=DataAssetType.CALIBRATION_SIGNAL_DATA,
        )
    )
    assert source.source_mode == "sibling_repo_static_export"


def test_demo_data_source_ref_construction() -> None:
    source = DataSourceRef(
        **_base_source_kwargs(
            source_mode=DataSourceMode.SAMPLE_DEMO_DATA,
            source_type=DataSourceType.DEMO_FIXTURE,
            uri_or_table_ref="demo://fixtures/national_mmm/outcome.csv",
            status=DataSourceStatus.DECLARED,
            declared_grain=DataGrain.WEEKLY,
            declared_geo_grain=GeoGrain.NATIONAL,
        )
    )
    assert source.source_mode == "sample_demo_data"
    assert source.status == "declared"


def test_specialized_source_ref_rejects_wrong_mode() -> None:
    with pytest.raises(ValidationError):
        FileSourceRef(
            **_base_source_kwargs(
                source_mode=DataSourceMode.STREAMLIT_FILE_UPLOAD,
                source_type=DataSourceType.FILE,
            )
        )


def test_source_ref_does_not_read_files() -> None:
    source = FileSourceRef(
        **_base_source_kwargs(
            source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
            source_type=DataSourceType.FILE,
            uri_or_table_ref="/nonexistent/path/file.csv",
        )
    )
    payload = source.model_dump()
    assert payload["uri_or_table_ref"] == "/nonexistent/path/file.csv"
    assert "file contents" not in str(payload).lower()

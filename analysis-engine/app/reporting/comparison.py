"""Report Comparison Module."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.reporting.enums import ReportSection
from app.reporting.exceptions import ReportGenerationError
from app.reporting.models import AnalysisReport


class ReportSectionDifference(BaseModel):
    """Immutable DTO holding differences details for a single ReportSection."""

    section: ReportSection = Field(..., description="The category type of this section.")
    title_changed: bool = Field(..., description="Flag indicating if the section header title changed.")
    content_changed: bool = Field(..., description="Flag indicating if the body content changed.")
    old_content: str = Field(..., description="Body content of the section in the old report.")
    new_content: str = Field(..., description="Body content of the section in the new report.")
    metadata_differences: Mapping[str, Any] = Field(
        default_factory=dict, description="Detailed dictionary of changes in section metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("metadata_differences", mode="after")
    @classmethod
    def freeze_metadata_differences(cls, v: Any) -> Any:
        """Enforces immutable mapping view on metadata differences."""
        return MappingProxyType(dict(v))


class ReportComparison(BaseModel):
    """Immutable DTO containing the complete aggregate comparison report."""

    project_name: str = Field(..., min_length=1, description="Analyzed project name identifier.")
    old_report_id: uuid.UUID = Field(..., description="UUID of the baseline report.")
    new_report_id: uuid.UUID = Field(..., description="UUID of the compared report.")
    compared_at: datetime = Field(..., description="UTC timezone-aware comparison execution timestamp.")

    added_sections: Tuple[ReportSection, ...] = Field(
        default_factory=tuple, description="Sections added in the new report."
    )
    removed_sections: Tuple[ReportSection, ...] = Field(
        default_factory=tuple, description="Sections removed in the new report."
    )
    modified_sections: Tuple[ReportSection, ...] = Field(
        default_factory=tuple, description="Sections modified in the new report."
    )
    unchanged_sections: Tuple[ReportSection, ...] = Field(
        default_factory=tuple, description="Sections completely unchanged in the new report."
    )

    section_differences: Mapping[ReportSection, ReportSectionDifference] = Field(
        default_factory=dict, description="Detailed changes mappings indexed by section."
    )

    metadata_changed: bool = Field(..., description="Flag indicating if report metadata changed.")
    metadata_differences: Mapping[str, Any] = Field(
        default_factory=dict, description="Detailed mappings of extra info and metadata changes."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("project_name", mode="after")
    @classmethod
    def validate_non_empty_project_name(cls, v: str) -> str:
        """Asserts project_name is not empty or whitespace-only."""
        if not v.strip():
            raise ValueError("project_name must not be empty or whitespace-only.")
        return v

    @field_validator("compared_at", mode="after")
    @classmethod
    def validate_utc_timestamp(cls, v: datetime) -> datetime:
        """Asserts that the timestamp is timezone-aware and set to UTC timezone."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("compared_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("section_differences", mode="after")
    @classmethod
    def freeze_section_differences(cls, v: Any) -> Any:
        """Enforces immutable mapping view on section differences."""
        return MappingProxyType(dict(v))

    @field_validator("metadata_differences", mode="after")
    @classmethod
    def freeze_metadata_differences(cls, v: Any) -> Any:
        """Enforces immutable mapping view on metadata differences."""
        return MappingProxyType(dict(v))


class ReportComparisonEngine:
    """Orchestrator for comparing two AnalysisReports and generating deterministic comparison DTOs."""

    def compare(
        self, old_report: AnalysisReport, new_report: AnalysisReport
    ) -> ReportComparison:
        """Compares two AnalysisReports deterministically and returns a ReportComparison DTO."""
        if old_report is None or new_report is None:
            raise ReportGenerationError("Both old_report and new_report must be provided.")
        if not isinstance(old_report, AnalysisReport) or not isinstance(
            new_report, AnalysisReport
        ):
            raise ReportGenerationError("Inputs must be instances of AnalysisReport.")

        # 1. Compare Metadata Fields
        meta_diff: Dict[str, Any] = {}
        metadata_changed = False

        if old_report.metadata.project_name != new_report.metadata.project_name:
            metadata_changed = True
            meta_diff["project_name"] = {
                "old": old_report.metadata.project_name,
                "new": new_report.metadata.project_name,
            }

        if old_report.metadata.format != new_report.metadata.format:
            metadata_changed = True
            meta_diff["format"] = {
                "old": old_report.metadata.format.value,
                "new": new_report.metadata.format.value,
            }

        # Compare extra_info dictionaries
        old_info = old_report.metadata.extra_info
        new_info = new_report.metadata.extra_info
        all_info_keys = set(old_info.keys()) | set(new_info.keys())

        for k in sorted(all_info_keys):
            if k not in old_info:
                metadata_changed = True
                meta_diff[f"extra_info_{k}"] = {"status": "added", "new_value": str(new_info[k])}
            elif k not in new_info:
                metadata_changed = True
                meta_diff[f"extra_info_{k}"] = {"status": "removed", "old_value": str(old_info[k])}
            elif old_info[k] != new_info[k]:
                metadata_changed = True
                meta_diff[f"extra_info_{k}"] = {
                    "status": "modified",
                    "old_value": str(old_info[k]),
                    "new_value": str(new_info[k]),
                }

        # 2. Compare Sections
        old_sec_keys = set(old_report.sections.keys())
        new_sec_keys = set(new_report.sections.keys())

        added = sorted(list(new_sec_keys - old_sec_keys), key=lambda x: x.value)
        removed = sorted(list(old_sec_keys - new_sec_keys), key=lambda x: x.value)
        
        modified = []
        unchanged = []
        sec_diffs: Dict[ReportSection, ReportSectionDifference] = {}

        shared_keys = old_sec_keys & new_sec_keys
        for sec in sorted(list(shared_keys), key=lambda x: x.value):
            old_s = old_report.sections[sec]
            new_s = new_report.sections[sec]

            title_changed = old_s.title != new_s.title
            content_changed = old_s.content != new_s.content

            # Diff section metadata
            sec_meta_diff: Dict[str, Any] = {}
            sec_meta_keys = set(old_s.metadata.keys()) | set(new_s.metadata.keys())
            for k in sorted(sec_meta_keys):
                if k not in old_s.metadata:
                    sec_meta_diff[k] = {"status": "added", "new_value": str(new_s.metadata[k])}
                elif k not in new_s.metadata:
                    sec_meta_diff[k] = {"status": "removed", "old_value": str(old_s.metadata[k])}
                elif old_s.metadata[k] != new_s.metadata[k]:
                    sec_meta_diff[k] = {
                        "status": "modified",
                        "old_value": str(old_s.metadata[k]),
                        "new_value": str(new_s.metadata[k]),
                    }

            is_modified = title_changed or content_changed or len(sec_meta_diff) > 0

            if is_modified:
                modified.append(sec)
                sec_diffs[sec] = ReportSectionDifference(
                    section=sec,
                    title_changed=title_changed,
                    content_changed=content_changed,
                    old_content=old_s.content,
                    new_content=new_s.content,
                    metadata_differences=sec_meta_diff,
                )
            else:
                unchanged.append(sec)

        # 3. Construct and return ReportComparison DTO
        return ReportComparison(
            project_name=new_report.metadata.project_name,
            old_report_id=old_report.id,
            new_report_id=new_report.id,
            compared_at=datetime.now(timezone.utc),
            added_sections=tuple(added),
            removed_sections=tuple(removed),
            modified_sections=tuple(modified),
            unchanged_sections=tuple(unchanged),
            section_differences=sec_diffs,
            metadata_changed=metadata_changed,
            metadata_differences=meta_diff,
        )

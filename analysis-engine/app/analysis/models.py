"""AI Analysis Domain Models module.

Defines immutable Pydantic v2 models representing code findings, AI recommendations,
run summaries, and full analysis results.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.analysis.enums import AnalysisSeverity, AnalysisType, RecommendationStatus


class AnalysisFinding(BaseModel):
    """Represents a specific design smell, vulnerability, or issue located in source code."""

    id: str = Field(..., description="Unique deterministic identifier for the finding.")
    title: str = Field(..., description="Short, human-readable summary of the issue.")
    description: str = Field(..., description="Detailed explanation of the problem.")
    severity: AnalysisSeverity = Field(..., description="Assigned impact severity level.")
    file_path: str = Field(..., description="Relative file path where the finding resides.")
    start_line: int = Field(..., ge=1, description="1-indexed starting line number.")
    end_line: int = Field(..., ge=1, description="1-indexed ending line number.")
    rule_id: Optional[str] = Field(default=None, description="Optional rule key identifier triggered.")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Extensible properties dictionary."
    )

    model_config = ConfigDict(frozen=True)


class AnalysisRecommendation(BaseModel):
    """Represents a recommendation or code fix generated to address a finding."""

    id: str = Field(..., description="Unique deterministic identifier for the recommendation.")
    finding_id: str = Field(..., description="ID of the finding this recommendation remediates.")
    remediation: str = Field(..., description="Description of instructions to fix the finding.")
    suggested_code: Optional[str] = Field(
        default=None, description="Optional suggested replacement code diff block."
    )
    status: RecommendationStatus = Field(
        default=RecommendationStatus.OPEN, description="Lifecycle status of recommendation."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Extensible metadata tags."
    )

    model_config = ConfigDict(frozen=True)


class AnalysisSummary(BaseModel):
    """Provides high-level totals and metadata about the analysis execution run."""

    total_findings: int = Field(..., ge=0, description="Sum of all findings generated.")
    findings_by_severity: Dict[str, int] = Field(
        default_factory=dict, description="Tally of findings grouped by severity category."
    )
    duration_ms: int = Field(default=0, ge=0, description="Total execution time in milliseconds.")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Extensible execution statistics."
    )

    model_config = ConfigDict(frozen=True)


class AnalysisResult(BaseModel):
    """Container payload containing all findings, recommendations, and statistics of a run."""

    id: str = Field(..., description="Unique run identifier.")
    analysis_type: AnalysisType = Field(..., description="Category of analysis performed.")
    summary: AnalysisSummary = Field(..., description="Aggregated totals and summary statistics.")
    findings: List[AnalysisFinding] = Field(
        default_factory=list, description="List of all detected source findings."
    )
    recommendations: List[AnalysisRecommendation] = Field(
        default_factory=list, description="List of generated remediation recommendations."
    )
    diagnostics: List[str] = Field(
        default_factory=list, description="Diagnostic logs describing analyzer run."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata tags describing analysis run settings."
    )

    model_config = ConfigDict(frozen=True)

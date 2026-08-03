"""AI Prompt Context Builder module.

Implements a stateless, deterministic builder that compiles and deduplicates structured
findings, recommendations, summaries, and reports into prompt-ready context models.
"""

from typing import Dict, List, Optional
import hashlib

from pydantic import BaseModel, ConfigDict, Field
from app.analysis.models import AnalysisResult
from app.analysis.report_builder import AnalysisReport


# --- Prompt Context Models ---


class PromptContextSection(BaseModel):
    """Represents a discrete context block prepared for inclusion in LLM prompts."""

    id: str = Field(..., description="Unique deterministic identifier for the context block.")
    title: str = Field(..., description="Human-readable title of the context block.")
    content: str = Field(..., description="Markdown content block text.")
    priority: int = Field(default=3, description="Priority weight (0=critical, 1=high, 2=med, 3=low).")

    model_config = ConfigDict(frozen=True)


class PromptContext(BaseModel):
    """Immutable collection of prompt-ready context blocks with stable serialization."""

    id: str = Field(..., description="Deterministic, hash-derived context run ID.")
    sections: List[PromptContextSection] = Field(
        default_factory=list, description="Sorted, unique context sections."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Execution parameters metadata."
    )

    model_config = ConfigDict(frozen=True)


# --- Prompt Context Builder ---


class PromptContextBuilder:
    """Stateless compiler that packages codebase analysis results for AI model ingestion."""

    def build_prompt_context(
        self,
        report: Optional[AnalysisReport] = None,
        result: Optional[AnalysisResult] = None,
        granularity: str = "detailed",
        *args,
        **kwargs,
    ) -> PromptContext:
        """Converts reports and results into a single consolidated, deduplicated PromptContext."""
        sections_dict: Dict[str, PromptContextSection] = {}

        # 1. Process AnalysisResult if provided
        if result:
            # Add Summary context
            summary_content = (
                f"Analysis Type: {result.analysis_type}\n"
                f"Total Findings: {result.summary.total_findings}\n"
            )
            if granularity == "detailed":
                summary_content += f"Severity Tallies: {result.summary.findings_by_severity}\n"
                summary_content += f"Summary Metadata: {result.summary.metadata}\n"

            sections_dict["summary-context"] = PromptContextSection(
                id="summary-context",
                title="Analysis Run Summary Context",
                content=summary_content.strip(),
                priority=1,  # High priority
            )

            # Add Findings Context
            findings_lines = []
            for f in result.findings:
                if granularity == "detailed":
                    findings_lines.append(
                        f"- [{f.severity.upper()}] {f.title} ({f.file_path}:L{f.start_line}): {f.description}"
                    )
                else:
                    findings_lines.append(f"- [{f.severity.upper()}] {f.title}")
            
            if findings_lines:
                sections_dict["findings-context"] = PromptContextSection(
                    id="findings-context",
                    title="Codebase Findings List",
                    content="## Findings List\n" + "\n".join(findings_lines),
                    priority=2,  # Medium priority
                )

            # Add Recommendations Context
            recs_lines = []
            for r in result.recommendations:
                if granularity == "detailed":
                    recs_lines.append(f"- Remediation: {r.remediation} (Finding: {r.finding_id})")
                    if r.suggested_code:
                        recs_lines.append(f"  Suggested Code Fix:\n```\n{r.suggested_code}\n```")
                else:
                    recs_lines.append(f"- Fix: {r.remediation}")

            if recs_lines:
                sections_dict["recs-context"] = PromptContextSection(
                    id="recs-context",
                    title="Remediation Actions",
                    content="## Remediation Strategy\n" + "\n".join(recs_lines),
                    priority=2,  # Medium priority
                )

        # 2. Process AnalysisReport if provided
        if report:
            for sec in report.sections:
                sid = f"report-sec-{sec.id}"
                # Handle potential duplicate sections by keeping the one with higher priority (or overwriting)
                sections_dict[sid] = PromptContextSection(
                    id=sid,
                    title=sec.title,
                    content=sec.content,
                    priority=3,  # Low/default priority for raw formatted report content
                )

        # 3. Sort sections deterministically: first by priority ascending, then by ID lexicographically
        sorted_sections = list(sections_dict.values())
        sorted_sections.sort(key=lambda x: (x.priority, x.id))

        # 4. Generate stable deterministic context ID based on combined contents
        combined_text = "".join(s.content for s in sorted_sections)
        h = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()[:12]
        context_id = f"prompt-context-{h}"

        return PromptContext(
            id=context_id,
            sections=sorted_sections,
            metadata={
                "granularity": granularity,
                "result_provided": str(result is not None),
                "report_provided": str(report is not None),
            },
        )

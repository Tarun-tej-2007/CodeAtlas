"""Quality AI Context Builder Module."""

from typing import List

from app.ai_service.context import AIContext, AIContextManager, ContextSection
from app.quality_analysis.enums import MetricCategory
from app.quality_analysis.models import QualityReport


class QualityAIContextBuilder:
    """Builder component that translates a QualityReport into structured, machine-readable AIContext."""

    def __init__(self, ai_context_manager: AIContextManager) -> None:
        """Initializes the context builder with dependency-injected AIContextManager."""
        if ai_context_manager is None:
            raise ValueError("AIContextManager dependency must not be None.")
        self.ai_context_manager = ai_context_manager

    def build_context(self, report: QualityReport) -> AIContext:
        """Translates a QualityReport into an immutable, structured AIContext."""
        # 1. Compile Metadata Map
        metadata = {
            "project_name": report.project_name,
            "generated_at": report.generated_at.isoformat(),
            "overall_score": report.summary.overall_score,
            "overall_level": report.summary.overall_level.value,
            **{f"weight_{k}": v for k, v in report.summary.metrics_by_category.items()},
        }

        # 2. Build Sections
        sections: List[ContextSection] = []

        # Section 1: Summary
        summary_lines = [
            f"Project: {report.project_name}",
            f"Generated At: {report.generated_at.isoformat()}",
            f"Overall Quality Score: {report.summary.overall_score:.2f}",
            f"Overall Quality Level: {report.summary.overall_level.value.upper()}",
            "Category Segment Averages:",
        ]
        for cat, avg in sorted(report.summary.metrics_by_category.items()):
            summary_lines.append(f"  {cat.value}: {avg:.2f}")

        sections.append(
            ContextSection(name="Summary", content="\n".join(summary_lines))
        )

        # Deterministically sort metrics by name to maintain output stability
        sorted_metrics = sorted(report.metrics, key=lambda x: x.name)

        # Section 2: Quality Metrics
        metric_lines = ["Quality Metrics Detail:"]
        for m in sorted_metrics:
            metric_lines.extend(
                [
                    f"- Name: {m.name}",
                    f"  Category: {m.category.value}",
                    f"  Value: {m.value:.2f}",
                    f"  Level: {m.level.value}",
                    f"  Description: {m.description}",
                    f"  Metadata: {dict(m.metadata)}",
                ]
            )
        sections.append(
            ContextSection(name="Quality Metrics", content="\n".join(metric_lines))
        )

        # Section 3: Maintainability metrics segment
        maint_metrics = [m for m in sorted_metrics if m.category == MetricCategory.MAINTAINABILITY]
        maint_lines = ["Maintainability Category Details:"]
        for m in maint_metrics:
            maint_lines.extend(
                [
                    f"- Name: {m.name}",
                    f"  Value: {m.value:.2f}",
                    f"  Level: {m.level.value}",
                    f"  Description: {m.description}",
                    f"  Metadata: {dict(m.metadata)}",
                ]
            )
        sections.append(
            ContextSection(name="Maintainability", content="\n".join(maint_lines))
        )

        # Section 4: Coupling & Cohesion metrics segment
        cc_metrics = [m for m in sorted_metrics if m.category in (MetricCategory.COUPLING, MetricCategory.COHESION)]
        cc_lines = ["Coupling & Cohesion Category Details:"]
        for m in cc_metrics:
            cc_lines.extend(
                [
                    f"- Name: {m.name}",
                    f"  Category: {m.category.value}",
                    f"  Value: {m.value:.2f}",
                    f"  Level: {m.level.value}",
                    f"  Description: {m.description}",
                    f"  Metadata: {dict(m.metadata)}",
                ]
            )
        sections.append(
            ContextSection(name="Coupling & Cohesion", content="\n".join(cc_lines))
        )

        # Section 5: Complexity metrics segment
        complex_metrics = [m for m in sorted_metrics if m.category == MetricCategory.COMPLEXITY]
        complex_lines = ["Complexity Category Details:"]
        for m in complex_metrics:
            complex_lines.extend(
                [
                    f"- Name: {m.name}",
                    f"  Value: {m.value:.2f}",
                    f"  Level: {m.level.value}",
                    f"  Description: {m.description}",
                    f"  Metadata: {dict(m.metadata)}",
                ]
            )
        sections.append(
            ContextSection(name="Complexity", content="\n".join(complex_lines))
        )

        # Section 6: Recommendations Input
        rec_lines = [
            f"Quality recommendation input requested for overall score {report.summary.overall_score:.2f} ({report.summary.overall_level.value}) in {report.project_name}."
        ]
        sections.append(
            ContextSection(name="Recommendations Input", content="\n".join(rec_lines))
        )

        # 3. Delegate Context Construction to AIContextManager
        return self.ai_context_manager.create_context(
            title=f"Quality Analysis Context: {report.project_name}",
            description=f"Structured context generated from quality report on {report.generated_at.isoformat()}.",
            metadata=metadata,
            sections=tuple(sections),
        )

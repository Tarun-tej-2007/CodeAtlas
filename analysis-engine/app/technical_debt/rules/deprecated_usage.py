"""Deprecated Usage Rule Module."""

from typing import Any, Iterable, List

from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity
from app.technical_debt.models import TechnicalDebtItem
from app.technical_debt.rule import TechnicalDebtRule


class DeprecatedUsageRule(TechnicalDebtRule):
    """Detects usage of symbols marked as deprecated in target metadata."""

    @property
    def rule_id(self) -> str:
        return "deprecated-usage-detection"

    @property
    def category(self) -> TechnicalDebtCategory:
        return TechnicalDebtCategory.DEPRECATED_USAGE

    @property
    def severity(self) -> TechnicalDebtSeverity:
        return TechnicalDebtSeverity.MEDIUM

    @property
    def title(self) -> str:
        return "Deprecated Symbol Usage"

    @property
    def description(self) -> str:
        return "The code references a symbol that has been marked as deprecated, indicating deprecated usage."

    def evaluate(self, context: Any, **kwargs) -> Iterable[TechnicalDebtItem]:
        """Evaluates references to deprecated symbols and returns technical debt items."""
        resolved_refs = self._get_resolved_references(context)

        findings: List[TechnicalDebtItem] = []
        for ref in resolved_refs:
            if not hasattr(ref, "target_symbol") or not ref.target_symbol:
                continue

            target = ref.target_symbol
            metadata = getattr(target, "metadata", {}) or {}

            # Detect deprecation markers in target metadata
            is_deprecated = metadata.get("deprecated") or metadata.get("is_deprecated")
            if is_deprecated:
                # Retrieve reference usage location
                file_path = None
                start_line = None
                if hasattr(ref, "reference") and ref.reference:
                    ref_loc = getattr(ref.reference, "location", None)
                    if ref_loc:
                        file_path = ref_loc.file_path.as_posix()
                        if hasattr(ref_loc, "location") and ref_loc.location:
                            start_line = ref_loc.location.start_line

                findings.append(
                    TechnicalDebtItem(
                        id=f"deprecated-use-{target.id}-{start_line or 0}",
                        category=self.category,
                        severity=self.severity,
                        title=f"Deprecated Symbol Usage: {target.name}",
                        description=(
                            f"Usage of deprecated symbol '{target.qualified_name}' "
                            f"(deprecation info: {is_deprecated})."
                        ),
                        effort_minutes=15,
                        location_file=file_path,
                        location_line=start_line,
                        metadata={
                            "target_symbol_id": target.id,
                            "deprecation_info": str(is_deprecated),
                        },
                    )
                )

        # Sort output deterministically
        return sorted(findings, key=lambda x: (x.location_file or "", x.location_line or 0, x.id))

    def _get_resolved_references(self, context: Any) -> list:
        if context is None:
            return []
        if hasattr(context, "resolved_references") and isinstance(context.resolved_references, list):
            return context.resolved_references
        if hasattr(context, "original_result"):
            orig = context.original_result
            if hasattr(orig, "reference_resolution_result"):
                ref_res = orig.reference_resolution_result
                if hasattr(ref_res, "resolved_references"):
                    return ref_res.resolved_references or []
        if hasattr(context, "reference_resolution_result"):
            ref_res = context.reference_resolution_result
            if hasattr(ref_res, "resolved_references"):
                return ref_res.resolved_references or []
        return []

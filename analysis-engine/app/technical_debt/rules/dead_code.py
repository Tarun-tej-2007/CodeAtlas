"""Dead Code Rule Module."""

from typing import Any, Iterable, List, Set

from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity
from app.technical_debt.models import TechnicalDebtItem
from app.technical_debt.rule import TechnicalDebtRule


class DeadCodeRule(TechnicalDebtRule):
    """Detects unused project symbols by checking if they are targets of resolved references."""

    @property
    def rule_id(self) -> str:
        return "dead-code-detection"

    @property
    def category(self) -> TechnicalDebtCategory:
        return TechnicalDebtCategory.DEAD_CODE

    @property
    def severity(self) -> TechnicalDebtSeverity:
        return TechnicalDebtSeverity.HIGH

    @property
    def title(self) -> str:
        return "Unused Declared Symbol"

    @property
    def description(self) -> str:
        return "A symbol is declared in the codebase but never referenced, indicating potential dead code."

    def evaluate(self, context: Any, **kwargs) -> Iterable[TechnicalDebtItem]:
        """Evaluates unused symbols and returns corresponding technical debt items."""
        # 1. Resolve files and references from context
        files = self._get_project_files(context)
        resolved_refs = self._get_resolved_references(context)

        if not files:
            return []

        # 2. Collect all target symbol IDs that are referenced
        referenced_ids: Set[str] = set()
        for ref in resolved_refs:
            if hasattr(ref, "target_symbol") and ref.target_symbol:
                referenced_ids.add(ref.target_symbol.id)

        # 3. Locate unused symbols
        findings: List[TechnicalDebtItem] = []
        for file in files.values():
            if not hasattr(file, "symbols") or not file.symbols:
                continue

            for symbol in file.symbols:
                # Exclude modules/namespaces from being flagged as dead code directly
                if hasattr(symbol, "kind") and symbol.kind.value in ("module", "namespace", "unknown"):
                    continue

                if symbol.id not in referenced_ids:
                    # Retrieve coordinates
                    file_path = None
                    start_line = None
                    if hasattr(symbol, "location") and symbol.location:
                        file_path = symbol.location.file_path.as_posix()
                        if hasattr(symbol.location, "location") and symbol.location.location:
                            start_line = symbol.location.location.start_line

                    findings.append(
                        TechnicalDebtItem(
                            id=f"dead-code-{symbol.id}",
                            category=self.category,
                            severity=self.severity,
                            title=f"Unused Symbol: {symbol.name}",
                            description=(
                                f"The symbol '{symbol.qualified_name}' of kind '{symbol.kind.value}' "
                                "is declared but never referenced."
                            ),
                            effort_minutes=15,
                            location_file=file_path,
                            location_line=start_line,
                            metadata={"symbol_id": symbol.id, "kind": symbol.kind.value},
                        )
                    )

        # 4. Deterministically sort findings for output stability
        return sorted(findings, key=lambda x: (x.location_file or "", x.location_line or 0, x.id))

    def _get_project_files(self, context: Any) -> dict:
        if context is None:
            return {}
        if hasattr(context, "files") and isinstance(context.files, dict):
            return context.files
        if hasattr(context, "original_result") and hasattr(context.original_result, "files"):
            return context.original_result.files or {}
        if hasattr(context, "semantic_context") and hasattr(context.semantic_context, "files"):
            return context.semantic_context.files or {}
        return {}

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

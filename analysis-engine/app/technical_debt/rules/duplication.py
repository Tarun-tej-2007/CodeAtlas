"""Duplication Rule Module."""

import linecache
from typing import Any, Dict, Iterable, List

from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity
from app.technical_debt.models import TechnicalDebtItem
from app.technical_debt.rule import TechnicalDebtRule


class DuplicationRule(TechnicalDebtRule):
    """Detects duplicate function/method implementations by comparing code blocks."""

    @property
    def rule_id(self) -> str:
        return "duplication-detection"

    @property
    def category(self) -> TechnicalDebtCategory:
        return TechnicalDebtCategory.DUPLICATION

    @property
    def severity(self) -> TechnicalDebtSeverity:
        return TechnicalDebtSeverity.HIGH

    @property
    def title(self) -> str:
        return "Duplicate Code Block"

    @property
    def description(self) -> str:
        return "Identical method or function implementations detected across different scopes or files."

    def evaluate(self, context: Any, **kwargs) -> Iterable[TechnicalDebtItem]:
        """Evaluates duplicate code implementations and returns technical debt items."""
        files = self._get_project_files(context)
        if not files:
            return []

        # 1. Gather all functions/methods and read their code blocks
        code_groups: Dict[str, List[Any]] = {}
        for file in files.values():
            if not hasattr(file, "symbols") or not file.symbols:
                continue

            for symbol in file.symbols:
                if not hasattr(symbol, "kind") or symbol.kind.value not in ("function", "method"):
                    continue

                # Ensure minimum size threshold of 4 lines to filter out small boilerplate
                start_line = None
                end_line = None
                if hasattr(symbol, "location") and symbol.location:
                    loc = getattr(symbol.location, "location", None)
                    if loc:
                        start_line = loc.start_line
                        end_line = loc.end_line

                if start_line is not None and end_line is not None:
                    if (end_line - start_line + 1) < 4:
                        continue

                code = self._read_symbol_code(symbol)
                if not code:
                    continue

                code_groups.setdefault(code, []).append(symbol)

        # 2. Flag duplicate implementations
        findings: List[TechnicalDebtItem] = []
        for code_text, symbols in code_groups.items():
            if len(symbols) <= 1:
                continue

            # Sort duplicates deterministically to treat the first definition as original
            sorted_symbols = sorted(symbols, key=lambda x: (x.location.file_path.as_posix(), x.location.location.start_line, x.id))

            # The first symbol is considered the "original" copy, others are flagged as duplicates
            original = sorted_symbols[0]
            for duplicate in sorted_symbols[1:]:
                file_path = duplicate.location.file_path.as_posix()
                start_line = duplicate.location.location.start_line

                findings.append(
                    TechnicalDebtItem(
                        id=f"duplicate-code-{duplicate.id}",
                        category=self.category,
                        severity=self.severity,
                        title=f"Duplicate Code Block: {duplicate.name}",
                        description=(
                            f"The symbol '{duplicate.qualified_name}' has an identical implementation "
                            f"to symbol '{original.qualified_name}' located in '{original.location.file_path.as_posix()}' "
                            f"on line {original.location.location.start_line}."
                        ),
                        effort_minutes=20,
                        location_file=file_path,
                        location_line=start_line,
                        metadata={
                            "original_symbol_id": original.id,
                            "duplicate_symbol_id": duplicate.id,
                        },
                    )
                )

        # Sort output deterministically
        return sorted(findings, key=lambda x: (x.location_file or "", x.location_line or 0, x.id))

    def _read_symbol_code(self, symbol: Any) -> str:
        """Reads symbol code from metadata or linecache fallback."""
        if hasattr(symbol, "metadata") and symbol.metadata:
            code = symbol.metadata.get("source") or symbol.metadata.get("code")
            if code:
                return str(code).strip()

        if not hasattr(symbol, "location") or not symbol.location:
            return ""
        file_path = symbol.location.file_path
        loc = getattr(symbol.location, "location", None)
        if not loc:
            return ""

        lines = []
        for line_no in range(loc.start_line, loc.end_line + 1):
            line = linecache.getline(str(file_path), line_no)
            if line:
                lines.append(line)
        return "".join(lines).strip()

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

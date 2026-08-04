"""AI Context Composer Engine module.

Combines, deduplicates, and priorities repository and symbol level AI context blocks
into a single structured context payload.
"""

from typing import Dict, List, Optional
import hashlib

from app.ai.enums import ContextPriority, ContextType, SummaryGranularity
from app.ai.models import ContextSection, SymbolContext, AIContextResult


from app.ai.cache import ContextLookupCache


class AIContextComposer:
    """Stateless engine responsible for composing multiple AIContextResult inputs into a single DTO."""

    # Define strict priority ordering (lower value = higher importance)
    PRIORITY_ORDER = {
        ContextPriority.CRITICAL: 0,
        ContextPriority.HIGH: 1,
        ContextPriority.MEDIUM: 2,
        ContextPriority.LOW: 3,
    }

    def compose(
        self,
        repo_result: Optional[AIContextResult] = None,
        symbol_result: Optional[AIContextResult] = None,
        cache: Optional[ContextLookupCache] = None,
        *args,
        **kwargs,
    ) -> AIContextResult:
        """Merges repository context and symbol contexts.

        Sections are deduplicated by section ID, keeping the block with the higher priority,
        and then sorted deterministically first by priority importance and then by ID.
        """
        diagnostics: List[str] = ["Started context composition pipeline."]

        combined_sections: List[ContextSection] = []
        combined_symbols: List[SymbolContext] = []
        repo_dto = None
        composed_metadata: Dict[str, str] = {}
        context_type = ContextType.SEMANTIC
        granularity = SummaryGranularity.COMPACT

        # 1. Process Repository Result
        if repo_result:
            context_type = repo_result.context_type
            granularity = repo_result.granularity
            combined_sections.extend(repo_result.sections)
            if repo_result.repository:
                repo_dto = repo_result.repository
            composed_metadata.update(repo_result.metadata)
            diagnostics.extend(repo_result.diagnostics)

        # 2. Process Symbol Result
        if symbol_result:
            # If symbol_result is provided, we can upgrade the context type and granularity if relevant
            if not repo_result:
                context_type = symbol_result.context_type
                granularity = symbol_result.granularity
            else:
                context_type = ContextType.SEMANTIC
                
            combined_sections.extend(symbol_result.sections)
            combined_symbols.extend(symbol_result.symbols)
            composed_metadata.update(symbol_result.metadata)
            diagnostics.extend(symbol_result.diagnostics)

        # 3. Deduplicate sections by section ID
        # If there are duplicates, keep the one with higher priority (lower order value)
        unique_sections: Dict[str, ContextSection] = {}
        for section in combined_sections:
            sid = section.id
            if sid not in unique_sections:
                unique_sections[sid] = section
            else:
                existing = unique_sections[sid]
                curr_prio = self.PRIORITY_ORDER.get(section.priority, 99)
                ex_prio = self.PRIORITY_ORDER.get(existing.priority, 99)
                if curr_prio < ex_prio:
                    unique_sections[sid] = section

        # Convert back to list and sort deterministically:
        # First by priority value (descending priority importance), then by ID lexicographically.
        final_sections = list(unique_sections.values())
        final_sections.sort(
            key=lambda x: (self.PRIORITY_ORDER.get(x.priority, 99), x.id)
        )

        # Sort symbols deterministically by qualified name
        final_symbols = sorted(combined_symbols, key=lambda x: x.qualified_name)

        # Deduplicate diagnostic lines while preserving order
        seen_diag = set()
        final_diagnostics = []
        for d in diagnostics:
            if d not in seen_diag:
                seen_diag.add(d)
                final_diagnostics.append(d)

        # Generate a deterministic stable ID for this run using MD5 hash of sections content
        sections_str = "".join(s.content for s in final_sections)
        run_hash = hashlib.md5(sections_str.encode("utf-8")).hexdigest()[:12]
        run_id = f"composed-context-run-{run_hash}"

        final_diagnostics.append(
            f"Successfully composed context. FinalSections={len(final_sections)}, FinalSymbols={len(final_symbols)}."
        )

        return AIContextResult(
            id=run_id,
            context_type=context_type,
            granularity=granularity,
            sections=final_sections,
            symbols=final_symbols,
            repository=repo_dto,
            diagnostics=final_diagnostics,
            metadata=composed_metadata,
        )

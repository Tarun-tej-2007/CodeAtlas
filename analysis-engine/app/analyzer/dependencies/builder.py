"""Dependency builder module.

Provides the DependencyBuilder class responsible for merging, deduplicating,
and building deterministic Dependency and ModuleDependency objects.
"""

from pathlib import Path
from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.exceptions import DependencyAnalysisError
from app.analyzer.dependencies.models import (
    Dependency,
    DependencyKind,
    DependencyResult,
    ModuleDependency,
)
from app.analyzer.models import AnalysisContext
from app.analyzer.resolution.models import ResolutionResult


class DependencyBuilder:
    """Merges and deduplicates dependency relationships from static analysis stages."""

    def __init__(self) -> None:
        """Initializes DependencyBuilder."""
        self._dep_counter = 0
        self._mod_dep_counter = 0

    def _generate_dep_id(self, kind: DependencyKind, source_id: str, line: int) -> str:
        self._dep_counter += 1
        clean_src = source_id.replace("/", "_").replace(".", "_").replace("\\", "_")
        return f"dep_{line}_{kind.value}_{clean_src}_{self._dep_counter}"

    def _generate_mod_dep_id(self, kind: DependencyKind, target_module: str) -> str:
        self._mod_dep_counter += 1
        clean_target = target_module.replace("/", "_").replace(".", "_").replace("-", "_")
        return f"moddep_{kind.value}_{clean_target}_{self._mod_dep_counter}"

    def build(
        self,
        context: AnalysisContext,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> DependencyResult:
        """Merges analysis outputs into deduplicated DependencyResult.

        Args:
            context: AnalysisContext containing ModuleMetadata and document info.
            resolution_result: Optional ResolutionResult containing resolved references.
            call_result: Optional CallAnalysisResult containing call references.

        Returns:
            An immutable DependencyResult model.

        Raises:
            DependencyAnalysisError: If building dependencies fails.
        """
        try:
            dependencies: list[Dependency] = []
            module_dependencies: list[ModuleDependency] = []

            seen_deps: set[tuple[str, str | None, DependencyKind, int]] = set()
            seen_mod_deps: set[tuple[str, str, DependencyKind]] = set()

            doc_path = context.ast_document.path

            # 1. Process Call Invocations -> DependencyKind.CALL
            if call_result:
                for call in call_result.calls:
                    source_id = call.caller_symbol_id or str(doc_path)
                    target_id = call.callee_symbol_id or call.callee_name
                    sig = (source_id, target_id, DependencyKind.CALL, call.line)

                    if sig not in seen_deps:
                        seen_deps.add(sig)
                        dep_id = self._generate_dep_id(DependencyKind.CALL, source_id, call.line)
                        dependencies.append(
                            Dependency(
                                id=dep_id,
                                source_id=source_id,
                                target_id=target_id,
                                kind=DependencyKind.CALL,
                                path=doc_path,
                                line=call.line,
                                resolved=call.resolved,
                            )
                        )

            # 2. Process Intra-file Symbol References -> DependencyKind.REFERENCE
            if resolution_result:
                for ref in resolution_result.references:
                    source_id = str(doc_path)
                    target_id = ref.resolved_symbol_id or ref.name
                    sig = (source_id, target_id, DependencyKind.REFERENCE, ref.line)

                    if sig not in seen_deps:
                        seen_deps.add(sig)
                        dep_id = self._generate_dep_id(DependencyKind.REFERENCE, source_id, ref.line)
                        dependencies.append(
                            Dependency(
                                id=dep_id,
                                source_id=source_id,
                                target_id=target_id,
                                kind=DependencyKind.REFERENCE,
                                path=doc_path,
                                line=ref.line,
                                resolved=ref.resolved,
                            )
                        )

            # 3. Process Module Imports and Exports -> ModuleDependency
            if context.module_metadata:
                source_mod = str(context.ast_document.relative_path)

                for imp in context.module_metadata.imports:
                    sig = (source_mod, imp.module, DependencyKind.IMPORT)
                    if sig not in seen_mod_deps:
                        seen_mod_deps.add(sig)
                        mod_dep_id = self._generate_mod_dep_id(DependencyKind.IMPORT, imp.module)
                        module_dependencies.append(
                            ModuleDependency(
                                id=mod_dep_id,
                                source_module=source_mod,
                                target_module=imp.module,
                                kind=DependencyKind.IMPORT,
                            )
                        )

                for exp in context.module_metadata.exports:
                    target_mod = exp.alias if (exp.kind == DependencyKind.EXPORT or exp.name == "*") and exp.alias else exp.name
                    sig = (source_mod, target_mod, DependencyKind.EXPORT)
                    if sig not in seen_mod_deps:
                        seen_mod_deps.add(sig)
                        mod_dep_id = self._generate_mod_dep_id(DependencyKind.EXPORT, target_mod)
                        module_dependencies.append(
                            ModuleDependency(
                                id=mod_dep_id,
                                source_module=source_mod,
                                target_module=target_mod,
                                kind=DependencyKind.EXPORT,
                            )
                        )


            resolved_count = sum(1 for d in dependencies if d.resolved)
            unresolved_count = sum(1 for d in dependencies if not d.resolved)

            return DependencyResult(
                dependencies=dependencies,
                module_dependencies=module_dependencies,
                dependency_count=len(dependencies),
                resolved_count=resolved_count,
                unresolved_count=unresolved_count,
            )
        except Exception as err:
            raise DependencyAnalysisError(
                f"Failed to build dependencies for '{context.ast_document.path}': {err}"
            ) from err

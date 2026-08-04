"""Abstract Semantic Architecture Rule module."""

from abc import ABC, abstractmethod
from typing import Tuple

from app.architecture_analysis.models import ArchitectureIssue
from app.architecture_analysis.rule import ArchitectureRule
from app.architecture_analysis.semantic_context import ArchitectureSemanticContext


class SemanticArchitectureRule(ArchitectureRule, ABC):
    """Abstract Base Class for architecture rules requiring codebase semantic context details."""

    @abstractmethod
    def evaluate_semantic(
        self, context: ArchitectureSemanticContext, *args, **kwargs
    ) -> Tuple[ArchitectureIssue, ...]:
        """Evaluates the rule constraints using the typed semantic context adapter."""
        pass

    def evaluate(self, *args, **kwargs) -> Tuple[ArchitectureIssue, ...]:
        """Implements standard rule evaluation by extracting or wrapping semantic context."""
        context = args[0] if args else kwargs.get("context")
        if context is None:
            return ()

        # Resolve or wrap semantic context adapter
        if isinstance(context, ArchitectureSemanticContext):
            semantic_ctx = context
        elif hasattr(context, "semantic_context") and isinstance(
            context.semantic_context, ArchitectureSemanticContext
        ):
            semantic_ctx = context.semantic_context
        else:
            try:
                semantic_ctx = ArchitectureSemanticContext(context)
            except Exception:
                return ()

        return self.evaluate_semantic(semantic_ctx, *args, **kwargs)
class_config = None

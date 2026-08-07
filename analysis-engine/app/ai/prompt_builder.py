"""Prompt Construction Service transforming AIContext into PromptContext."""

from typing import Any, Dict, Optional

from app.ai.enums import AIAnalysisType
from app.ai.exceptions import AIValidationError
from app.ai.interfaces import PromptBuilder
from app.ai.models import AIContext, AIRequest, PromptContext

# System prompts per analysis type classification
SYSTEM_INSTRUCTIONS: Dict[AIAnalysisType, str] = {
    AIAnalysisType.FULL_ARCHITECTURE_REVIEW: (
        "You are an elite software architect performing a full architecture review. "
        "Analyze the layering, dependencies, design smells, decisions, and governance rules. "
        "Produce detailed architectural alignment insights."
    ),
    AIAnalysisType.REFACTORING_REVIEW: (
        "You are an expert refactoring coach. Analyze the codebase dependency connections, "
        "smells, and coupling metrics to identify feature envy, god components, or cyclical modules. "
        "Provide step-by-step refactoring recommendations."
    ),
    AIAnalysisType.SECURITY_REVIEW: (
        "You are a principal security architect. Analyze architectural boundaries, layering violations, "
        "and governance conflicts. Spot structural security design flaws and untrusted boundary links."
    ),
    AIAnalysisType.PERFORMANCE_REVIEW: (
        "You are a performance engineer. Analyze module coupling, dependency topology, and complexity metrics. "
        "Look for cycles, bottlenecks, and structural overhead in the graph."
    ),
    AIAnalysisType.TECHNICAL_DEBT_REVIEW: (
        "You are a technical debt analyst. Evaluate codebase issues, coupling trends, stability delta, "
        "and code smells. Highlight maintainability hotspots and high-remediation-effort areas."
    ),
    AIAnalysisType.GOVERNANCE_REVIEW: (
        "You are an architecture compliance officer. Analyze policy rule violations, layering conflicts, "
        "and governance failures. Identify specific violations of the defined architecture guidelines."
    ),
    AIAnalysisType.ADR_REVIEW: (
        "You are an ADR quality reviewer. Analyze the Architecture Decision Records (ADRs) context summary, "
        "completeness, lifecycle status, and design drift. Recommend alignment corrections."
    ),
    AIAnalysisType.CUSTOM: (
        "You are a custom AI architecture analyst. Review the provided codebase structure context "
        "according to the custom directives specified."
    ),
}


class PromptBuilderService(PromptBuilder):
    """Concrete PromptBuilder generating deterministic, optimized PromptContext objects."""

    def __init__(self) -> None:
        """Initializes the prompt builder service."""
        pass

    def build_prompt(self, request: AIRequest, context: AIContext) -> PromptContext:
        """Transforms AIContext and request instructions into an immutable PromptContext.

        Args:
            request: The AIRequest session directives.
            context: Collected codebase context.

        Returns:
            The compiled immutable PromptContext.

        Raises:
            AIValidationError: For invalid parameters.
        """
        # Fail-fast validations
        if request is None:
            raise AIValidationError("request must not be None.")
        if context is None:
            raise AIValidationError("context must not be None.")

        analysis_type = request.analysis_type
        if analysis_type not in SYSTEM_INSTRUCTIONS:
            raise AIValidationError(f"Unsupported analysis type: {analysis_type}")

        # Assemble system prompt sections deterministically
        system_base = SYSTEM_INSTRUCTIONS[analysis_type]
        context_parts = []

        # Scope overview
        if context.files_count > 0:
            context_parts.append(f"Total Scope Files: {context.files_count}")

        # Dependency Graph
        if context.dependency_graph_summary:
            context_parts.append("Dependency Graph Structure:\n" + context.dependency_graph_summary.strip())

        # Architecture issues
        if context.architecture_issues:
            issues_str = "\n".join(f" - {issue}" for issue in context.architecture_issues)
            context_parts.append("Architecture Issues:\n" + issues_str)

        # Governance violations
        if context.governance_violations:
            viol_str = "\n".join(f" - {viol}" for viol in context.governance_violations)
            context_parts.append("Governance Compliance Violations:\n" + viol_str)

        # ADRs
        if context.decisions_summary:
            dec_str = "\n".join(f" - {dec}" for dec in context.decisions_summary)
            context_parts.append("Architecture Decision Records (ADRs) Summary:\n" + dec_str)

        # Evolution Result
        evolution = context.extra_context.get("evolution")
        if evolution:
            context_parts.append("Architecture Evolution & Trends:\n" + str(evolution).strip())

        # Extra context variables
        for k in sorted(context.extra_context.keys()):
            if k == "evolution":
                continue
            v = context.extra_context[k]
            context_parts.append(f"Extra Context [{k}]:\n{v}")

        # Normalize whitespace and join sections
        context_str = "\n\n".join(part.strip() for part in context_parts if part)
        
        system_prompt = f"{system_base}\n\n=== CODEBASE CONTEXT ===\n{context_str}".strip()

        # Handle user prompt
        user_prompt = "Perform the architectural review and compile structured recommendations."
        if request.custom_instructions and request.custom_instructions.strip():
            user_prompt = request.custom_instructions.strip()

        # Deterministic token estimation (approx 4 chars per token)
        token_estimate = int((len(system_prompt) + len(user_prompt)) / 4)

        # Populate variables dictionary
        variables = {
            "token_estimate": token_estimate,
            "project_id": str(request.project_id),
            "commit_id": request.commit_id,
            "analysis_type": request.analysis_type.value,
        }

        return PromptContext(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            variables=variables,
        )

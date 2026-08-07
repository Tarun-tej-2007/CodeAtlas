"""Abstract interface definitions for AI Architecture Intelligence components."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from app.ai.models import (
    AIAnalysis,
    AIContext,
    AIRecommendation,
    AIRequest,
    AIUsageStatistics,
    PromptContext,
    ArchitectureReview,
    AIResult,
)


class AIContextBuilder(ABC):
    """Abstract interface defining the component that compiles codebase facts context."""

    @abstractmethod
    def build_context(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
        decisions: Optional[Tuple[Any, ...]] = None,
        **kwargs: Any,
    ) -> AIContext:
        """Assembles dependency summaries, quality issues, compliance violations, and ADRs into AIContext.

        Args:
            project_id: Associated project scoping UUID.
            commit_id: Baseline target commit hash.
            dependency_graph: Codebase dependency graph artifact.
            arch_result: Quality analyzer outputs.
            governance_result: Active compliance violations.
            evolution_result: Codebase history metrics.
            decisions: Collection of Architecture Decisions.

        Returns:
            The compiled immutable AIContext instance.

        Raises:
            AIContextError: If context collection fails.
        """
        pass


class PromptBuilder(ABC):
    """Abstract interface defining prompt generation and template interpolation component."""

    @abstractmethod
    def build_prompt(self, request: AIRequest, context: AIContext) -> PromptContext:
        """Interpolates prompts templates with input request directives and repository facts.

        Args:
            request: The AIRequest payload parameters.
            context: Collected facts and details inside AIContext.

        Returns:
            The compiled immutable PromptContext instance.

        Raises:
            PromptGenerationError: If prompt template parsing or variables interpolation fails.
        """
        pass


class LLMProvider(ABC):
    """Abstract interface defining downstream platform-agnostic communication contracts with LLM APIs."""

    @abstractmethod
    def generate_completion(self, request: AIRequest, prompt: PromptContext) -> Tuple[str, AIUsageStatistics]:
        """Dispatches system and user queries to the configured LLM API.

        Args:
            request: Session configuration metadata parameters.
            prompt: Formatted prompt queries input.

        Returns:
            A tuple of (raw response string, token usage statistics).

        Raises:
            AIProviderError: If external platform call fails.
        """
        pass


class RecommendationGenerator(ABC):
    """Abstract interface for parsing and translating raw text responses into structured recommendation DTOs."""

    @abstractmethod
    def generate_recommendations(
        self,
        request: AIRequest,
        raw_completion: str,
        analysis: Optional[AIAnalysis] = None,
        prompt_context: Optional[PromptContext] = None,
        ai_context: Optional[AIContext] = None,
    ) -> Tuple[AIRecommendation, ...]:
        """Translates raw LLM response text into structured AIRecommendation tuples.

        Args:
            request: Context request configuration metadata.
            raw_completion: Raw completion string returned by the LLM.

        Returns:
            An immutable tuple of AIRecommendation instances.

        Raises:
            AIValidationError: If formatting validation fails.
        """
        pass


class AIRepository(ABC):
    """Abstract interface defining data storage/retrieval operations for serialized AI subsystem artifacts."""

    @abstractmethod
    def save_data(self, key: str, data: dict) -> None:
        """Saves a data dictionary under a given key.

        Args:
            key: Target unique storage key string.
            data: Payload dictionary to save.

        Raises:
            Exception: If storage fails.
        """
        pass

    @abstractmethod
    def get_data(self, key: str) -> Optional[dict]:
        """Retrieves a data dictionary by key.

        Args:
            key: Target unique storage key string.

        Returns:
            The raw data dict if found, else None.

        Raises:
            Exception: If query fails.
        """
        pass

    @abstractmethod
    def delete_data(self, key: str) -> None:
        """Deletes data stored under a given key.

        Args:
            key: Target unique storage key string.

        Raises:
            Exception: If deletion fails.
        """
        pass

    @abstractmethod
    def list_keys(self, prefix: str) -> Tuple[str, ...]:
        """Lists all keys in storage matching a prefix.

        Args:
            prefix: Prefix to match keys.

        Returns:
            An immutable tuple of storage keys.

        Raises:
            Exception: If query fails.
        """
        pass


class AIAnalysisPersistence(ABC):
    """Abstract interface defining storage and retrieval contracts for AI analysis runs."""

    @abstractmethod
    def save_analysis(self, project_id: uuid.UUID, analysis: AIAnalysis) -> None:
        """Persists an AIAnalysis execution record.

        Args:
            project_id: Scoping project UUID.
            analysis: The AIAnalysis run instance.

        Raises:
            AIPersistenceError: If save fails.
        """
        pass

    @abstractmethod
    def get_analysis(self, analysis_id: uuid.UUID) -> Optional[AIAnalysis]:
        """Retrieves a previously persisted AIAnalysis execution record.

        Args:
            analysis_id: Target analysis execution UUID.

        Returns:
            AIAnalysis if found, else None.

        Raises:
            AIPersistenceError: If retrieval query fails.
        """
        pass

    @abstractmethod
    def list_analyses(self, project_id: uuid.UUID) -> Tuple[AIAnalysis, ...]:
        """Lists all AI analysis execution records associated with a project.

        Args:
            project_id: Target project UUID.

        Returns:
            An immutable tuple of AIAnalysis records.

        Raises:
            AIPersistenceError: If query fails.
        """
        pass

    @abstractmethod
    def save_result(self, project_id: uuid.UUID, result: AIResult) -> None:
        """Persists an AIResult execution record.

        Args:
            project_id: Scoping project UUID.
            result: The AIResult run instance.

        Raises:
            AIPersistenceError: If save fails.
        """
        pass

    @abstractmethod
    def get_result(self, project_id: uuid.UUID, commit_id: str) -> Optional[AIResult]:
        """Retrieves a previously persisted AIResult execution record by project and commit.

        Args:
            project_id: Scoping project UUID.
            commit_id: Associated commit hash.

        Returns:
            AIResult if found, else None.

        Raises:
            AIPersistenceError: If query fails.
        """
        pass

    @abstractmethod
    def list_results(self, project_id: uuid.UUID) -> Tuple[AIResult, ...]:
        """Lists all AIResult execution records associated with a project.

        Args:
            project_id: Target project UUID.

        Returns:
            An immutable tuple of AIResult records.

        Raises:
            AIPersistenceError: If query fails.
        """
        pass

    @abstractmethod
    def delete_result(self, project_id: uuid.UUID, commit_id: str) -> None:
        """Deletes an AIResult execution record.

        Args:
            project_id: Scoping project UUID.
            commit_id: Associated commit hash.

        Raises:
            AIPersistenceError: If deletion fails.
        """
        pass


class ArchitectureReviewer(ABC):
    """Abstract interface defining the component that synthesizes AI analysis results into reports."""

    @abstractmethod
    def generate_review(
        self,
        context: AIContext,
        analysis: AIAnalysis,
        recommendations: Tuple[AIRecommendation, ...],
    ) -> ArchitectureReview:
        """Synthesizes context, run history, and recommendations into an ArchitectureReview.

        Args:
            context: Collected codebase facts context.
            analysis: Associated AIAnalysis run details.
            recommendations: Set of resolved recommendations.

        Returns:
            The compiled immutable ArchitectureReview report.

        Raises:
            AIValidationError: If input validation fails.
        """
        pass


class AIOrchestrator(ABC):
    """Abstract interface defining the entry point for the AI Intelligence orchestration pipeline."""

    @abstractmethod
    def orchestrate_analysis(
        self,
        request: AIRequest,
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
        decisions: Optional[Tuple[Any, ...]] = None,
        **kwargs: Any,
    ) -> AIResult:
        """Runs the end-to-end AI review pipeline, aggregating facts, calling LLM, and generating recommendations.

        Args:
            request: The AIRequest parameters.
            dependency_graph: Optional dependency graph input.
            arch_result: Optional architectural analysis results.
            governance_result: Optional governance check results.
            evolution_result: Optional evolution trend results.
            decisions: Optional architecture decision records.
            **kwargs: Extra extensible analysis subsystem parameters.

        Returns:
            The immutable result DTO enclosing the AIAnalysis and compiled review report.

        Raises:
            AIValidationError: For request parameter failures.
            AIProviderError: For model execution provider failures.
            AIPersistenceError: For storage persisting failures.
        """
        pass

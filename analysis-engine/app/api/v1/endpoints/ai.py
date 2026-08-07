"""AI Architecture Intelligence REST API endpoints module."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.ai import (
    AIAnalysis,
    AIAnalysisType,
    AIContextAggregationService,
    AIOrchestratorService,
    AIProvider,
    AIRequest,
    AIResult,
    AIValidationError,
    AIProviderError,
    AIPersistenceError,
    AIAnalysisPersistenceService,
    AIRepository,
    ArchitectureReview,
    ArchitectureReviewService,
    PromptBuilderService,
    PromptContext,
    AIUsageStatistics,
    RecommendationGeneratorService,
    AIRecommendation,
    AIMetadata,
)
from app.ai.interfaces import LLMProvider
from app.graph.dependency_graph import DependencyGraph
from app.architecture.models import ArchitectureAnalysisResult
from app.governance.models import GovernanceResult
from app.decision.models import ArchitectureDecision


def verify_token(authorization: Optional[str] = Header(default=None)) -> str:
    """Dependency enforcing security token bearer authorization checks."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Only Bearer token is supported.",
        )
    token = authorization.split(" ")[1]
    if token != "supersecretjwtkey123!":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid security token.",
        )
    return token


router = APIRouter(prefix="/ai", dependencies=[Depends(verify_token)])


# Concrete mock LLMProvider for API execution
class MockLLMProvider(LLMProvider):
    """Mock LLMProvider implementing generate_completion returning deterministic recommendations."""

    def generate_completion(self, request: AIRequest, prompt: PromptContext) -> Tuple[str, AIUsageStatistics]:
        raw_response = """
        [
            {
                "title": "Fix layer breach",
                "description": "Database modules imported inside UI layer.",
                "category": "architecture",
                "priority": "critical",
                "affected_files": ["src/ui/app.py"],
                "confidence_score": 0.9,
                "reasoning": "Layering violation",
                "affected_components": ["UI Layer"],
                "suggested_actions": ["Move imports out of src/ui/app.py"]
            }
        ]
        """
        stats = AIUsageStatistics(prompt_tokens=50, completion_tokens=100, total_tokens=150)
        return raw_response, stats


def get_ai_repo(request: Request) -> AIRepository:
    """Retrieves or initializes the thread-safe in-memory AIRepository on the app state."""
    if not hasattr(request.app.state, "ai_repo"):
        from app.tests.test_ai_persistence import InMemoryAIRepository
        request.app.state.ai_repo = InMemoryAIRepository()
    return request.app.state.ai_repo


def get_persistence_service(repo: AIRepository = Depends(get_ai_repo)) -> AIAnalysisPersistenceService:
    """Dependency getter for the AIAnalysisPersistenceService."""
    return AIAnalysisPersistenceService(repo)


def get_ai_orchestrator(persistence: AIAnalysisPersistenceService = Depends(get_persistence_service)) -> AIOrchestratorService:
    """Dependency getter for the AIOrchestratorService."""
    context_builder = AIContextAggregationService()
    prompt_builder = PromptBuilderService()
    llm_provider = MockLLMProvider()
    recommendation_generator = RecommendationGeneratorService()
    architecture_reviewer = ArchitectureReviewService()

    return AIOrchestratorService(
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_provider=llm_provider,
        recommendation_generator=recommendation_generator,
        architecture_reviewer=architecture_reviewer,
        persistence=persistence,
    )


class AIAnalyzeRequestPayload(BaseModel):
    """Payload schema requesting full AI review pipeline execution."""

    project_id: uuid.UUID = Field(..., description="Unique project tracking UUID.")
    commit_id: str = Field(..., min_length=1, description="Target Git commit hash.")
    analysis_type: AIAnalysisType = Field(..., description="Focus type classification of analysis.")
    custom_instructions: Optional[str] = Field(default=None, description="Optional custom guidelines.")
    # Optional subsystem outputs
    dependency_graph: Optional[dict] = Field(default=None, description="Dependency graph dictionary payload.")
    arch_result: Optional[dict] = Field(default=None, description="Architecture metrics and smells payload.")
    governance_result: Optional[dict] = Field(default=None, description="Governance policies violations payload.")
    evolution_result: Optional[dict] = Field(default=None, description="Evolution trend delta metrics payload.")
    decisions: Optional[List[dict]] = Field(default=None, description="Architecture Decision Records payload list.")


@router.post("/analyze", response_model=AIResult, status_code=status.HTTP_201_CREATED)
def analyze_codebase(
    payload: AIAnalyzeRequestPayload,
    orchestrator: AIOrchestratorService = Depends(get_ai_orchestrator),
) -> AIResult:
    """End-to-end pipeline execution endpoint orchestrating aggregation, LLM prompts, and review compilation."""
    # Build AIRequest request session DTO
    time_now = datetime.now(timezone.utc)
    metadata = AIMetadata(
        author="API Client",
        created_at=time_now,
        provider=AIProvider.MOCK,
        model_name="mock-model",
        temperature=0.0,
    )
    request_dto = AIRequest(
        project_id=payload.project_id,
        commit_id=payload.commit_id,
        analysis_type=payload.analysis_type,
        custom_instructions=payload.custom_instructions,
        metadata=metadata,
    )

    # Deserialize optional subsystem outputs if provided
    dep_graph = None
    if payload.dependency_graph:
        dep_graph = DependencyGraph.model_validate(payload.dependency_graph)

    arch_res = None
    if payload.arch_result:
        arch_res = ArchitectureAnalysisResult.model_validate(payload.arch_result)

    gov_res = None
    if payload.governance_result:
        gov_res = GovernanceResult.model_validate(payload.governance_result)

    evol_res = None
    if payload.evolution_result:
        # Resolve between EvolutionResult and EvolutionTrendResult
        from app.evolution.models import EvolutionResult, EvolutionTrendResult
        if "changes" in payload.evolution_result or "changes_summary" in payload.evolution_result:
            evol_res = EvolutionResult.model_validate(payload.evolution_result)
        else:
            evol_res = EvolutionTrendResult.model_validate(payload.evolution_result)

    decs = None
    if payload.decisions:
        decs = tuple(ArchitectureDecision.model_validate(d) for d in payload.decisions)

    # Run orchestrator
    try:
        return orchestrator.orchestrate_analysis(
            request=request_dto,
            dependency_graph=dep_graph,
            arch_result=arch_res,
            governance_result=gov_res,
            evolution_result=evol_res,
            decisions=decs,
        )
    except AIValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AIProviderError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except AIPersistenceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected pipeline failure: {e}")


@router.get("/analysis/{analysis_id}", response_model=AIAnalysis)
def get_analysis_record(
    analysis_id: uuid.UUID,
    persistence: AIAnalysisPersistenceService = Depends(get_persistence_service),
) -> AIAnalysis:
    """Retrieves a previously stored AIAnalysis run record by ID."""
    try:
        rec = persistence.get_analysis(analysis_id)
    except AIPersistenceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AIAnalysis run with ID '{analysis_id}' not found.",
        )
    return rec


@router.get("/result/{analysis_id}", response_model=AIResult)
def get_analysis_result(
    analysis_id: uuid.UUID,
    persistence: AIAnalysisPersistenceService = Depends(get_persistence_service),
) -> AIResult:
    """Retrieves the complete AIResult containing analysis DTO and review report."""
    try:
        analysis = persistence.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AIAnalysis with ID '{analysis_id}' not found.",
            )
        result = persistence.get_result(analysis.project_id, analysis.commit_id)
    except AIPersistenceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AIResult associated with analysis '{analysis_id}' not found.",
        )
    return result


@router.get("/review/{analysis_id}", response_model=ArchitectureReview)
def get_architecture_review_report(
    analysis_id: uuid.UUID,
    persistence: AIAnalysisPersistenceService = Depends(get_persistence_service),
) -> ArchitectureReview:
    """Retrieves the generated ArchitectureReview report for a run."""
    result = get_analysis_result(analysis_id, persistence)
    review = result.extra_info.get("review")
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ArchitectureReview report for analysis '{analysis_id}' not found.",
        )
    return review


@router.get("/recommendations/{analysis_id}", response_model=List[AIRecommendation])
def get_analysis_recommendations(
    analysis_id: uuid.UUID,
    persistence: AIAnalysisPersistenceService = Depends(get_persistence_service),
) -> List[AIRecommendation]:
    """Retrieves the list of generated recommendations for a run."""
    analysis = get_analysis_record(analysis_id, persistence)
    return list(analysis.recommendations)

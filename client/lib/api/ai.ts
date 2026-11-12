import { apiClient } from "./client";

export type AIAnalysisType =
  | "comprehensive"
  | "security"
  | "maintainability"
  | "performance"
  | "architecture";

export interface AIAnalyzePayload {
  project_id: string;
  commit_id: string;
  analysis_type: AIAnalysisType;
  custom_instructions?: string;
  dependency_graph?: Record<string, unknown>;
  arch_result?: Record<string, unknown>;
  governance_result?: Record<string, unknown>;
  evolution_result?: Record<string, unknown>;
  decisions?: Array<Record<string, unknown>>;
}

export interface AIRecommendationItem {
  id?: string;
  title: string;
  description: string;
  category: string;
  priority: "critical" | "high" | "medium" | "low";
  affected_files?: string[];
  affected_components?: string[];
  confidence_score: number;
  reasoning?: string;
  suggested_actions?: string[];
}

export interface ArchitectureReviewData {
  review_id?: string;
  summary: string;
  findings?: Array<Record<string, unknown>>;
  score?: number;
  strengths?: string[];
}

export interface AIResultData {
  analysis_id: string;
  project_id: string;
  commit_id: string;
  recommendations: AIRecommendationItem[];
  extra_info?: {
    review?: ArchitectureReviewData;
  };
}

export async function submitAIReview(
  payload: AIAnalyzePayload
): Promise<AIResultData> {
  return apiClient<AIResultData>("/api/v1/ai/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getAIResult(
  analysisId: string
): Promise<AIResultData> {
  return apiClient<AIResultData>(`/api/v1/ai/result/${analysisId}`);
}

export async function getAIReview(
  analysisId: string
): Promise<ArchitectureReviewData> {
  return apiClient<ArchitectureReviewData>(`/api/v1/ai/review/${analysisId}`);
}

export async function getAIRecommendations(
  analysisId: string
): Promise<AIRecommendationItem[]> {
  return apiClient<AIRecommendationItem[]>(`/api/v1/ai/recommendations/${analysisId}`);
}

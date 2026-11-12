import { apiClient } from "./client";

export interface EvolutionRequest {
  project_id: string;
  project_name: string;
  source_commit: string;
  target_commit: string;
}

export interface ArchitectureSnapshotData {
  commit_id: string;
  timestamp: string;
  health_score?: number;
  drift_score?: number;
  metrics?: Record<string, unknown>;
  layers?: Array<Record<string, unknown>>;
}

export interface EvolutionResultData {
  evolution_id: string;
  metadata?: {
    project_name: string;
    source_commit: string;
    target_commit: string;
    created_at: string;
    status: string;
  };
  changes?: Array<Record<string, unknown>>;
  summary?: Record<string, unknown>;
  trends?: Record<string, unknown>;
  risk_report?: Record<string, unknown>;
}

export async function submitEvolutionAnalysis(
  payload: EvolutionRequest
): Promise<EvolutionResultData> {
  return apiClient<EvolutionResultData>("/api/v1/evolution/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getEvolutionSnapshot(
  commitId: string
): Promise<ArchitectureSnapshotData> {
  return apiClient<ArchitectureSnapshotData>(`/api/v1/evolution/snapshot/${commitId}`);
}

export async function getEvolutionResult(
  evolutionId: string
): Promise<EvolutionResultData> {
  return apiClient<EvolutionResultData>(`/api/v1/evolution/result/${evolutionId}`);
}

export async function getEvolutionTrend(
  evolutionId: string
): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>(`/api/v1/evolution/trend/${evolutionId}`);
}

export async function getEvolutionRiskReport(
  evolutionId: string
): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>(`/api/v1/evolution/risks/${evolutionId}`);
}

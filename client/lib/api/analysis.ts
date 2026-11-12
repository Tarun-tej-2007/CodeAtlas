import { apiClient } from "./client";
import { AnalysisResponse } from "@/types/analysis";

export interface SubmitAnalysisParams {
  repository_url: string;
  project_id: string;
  run_sync?: boolean;
}

export interface IncrementalAnalysisPayload {
  project_id: string;
  project_name: string;
  repository_root: string;
  source_commit: string;
  target_commit: string;
  nodes?: Array<Record<string, unknown>>;
  edges?: Array<Record<string, unknown>>;
}

export interface ChangedFileItem {
  path: string;
  change_type: string;
  impacted_dependencies?: string[];
}

export async function submitDirectAnalysis(
  params: SubmitAnalysisParams
): Promise<AnalysisResponse> {
  const qs = params.run_sync ? "?run_sync=true" : "";
  return apiClient<AnalysisResponse>(`/api/v1/analyze${qs}`, {
    method: "POST",
    body: JSON.stringify({
      repository_url: params.repository_url,
      project_id: params.project_id,
    }),
    targetService: "analysis",
  });
}

export async function submitIncrementalAnalysis(
  payload: IncrementalAnalysisPayload
): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>("/api/v1/incremental/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getIncrementalChanges(
  analysisId: string
): Promise<ChangedFileItem[]> {
  return apiClient<ChangedFileItem[]>(`/api/v1/incremental/changes/${analysisId}`);
}

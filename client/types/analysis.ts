export type AnalysisStatus = "accepted" | "running" | "completed" | "failed";

export interface AnalysisRequest {
  repository_url: string;
  project_id: string;
}

export interface AnalysisResponse {
  job_id: string;
  status: AnalysisStatus;
  message: string;
  project_id: string;
  repository_url: string;
  unified_result?: unknown;
  report_result?: unknown;
  dashboard_result?: unknown;
}

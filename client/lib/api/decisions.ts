import { apiClient } from "./client";

export interface DecisionRecord {
  id?: string;
  title: string;
  problem?: string;
  decision?: string;
  rationale?: string;
  status?: string;
  category?: string;
  priority?: string;
  impact?: string;
  effort?: string;
  confidence?: number;
  affected_components?: string[];
}

export interface DecisionAnalyzePayload {
  project_id: string;
  commit_id: string;
  requests?: DecisionRecord[];
}

export interface DecisionAnalysisResultData {
  project_id: string;
  commit_id: string;
  decisions?: DecisionRecord[];
  health_report?: Record<string, unknown>;
  drift_report?: Record<string, unknown>;
  trace_graph?: Record<string, unknown>;
}

export async function analyzeDecisions(
  payload: DecisionAnalyzePayload
): Promise<DecisionAnalysisResultData> {
  return apiClient<DecisionAnalysisResultData>("/api/v1/decision/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getDecision(decisionId: string): Promise<DecisionRecord> {
  return apiClient<DecisionRecord>(`/api/v1/decision/${decisionId}`);
}

export async function getDecisionTraceGraph(decisionId: string): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>(`/api/v1/decision/trace/${decisionId}`);
}

export async function getDecisionDriftReport(decisionId: string): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>(`/api/v1/decision/drift/${decisionId}`);
}

export async function getDecisionHealthReport(decisionId: string): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>(`/api/v1/decision/health/${decisionId}`);
}

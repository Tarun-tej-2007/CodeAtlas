import { apiClient } from "./client";

export interface GovernancePolicyRule {
  rule_id?: string;
  name: string;
  category: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  pattern?: string;
  description?: string;
}

export interface GovernancePolicy {
  policy_id: string;
  name: string;
  category: string;
  rules: GovernancePolicyRule[];
  description?: string;
  created_at?: string;
}

export interface GovernanceRequest {
  project_id: string;
  commit_id: string;
  policies?: GovernancePolicy[];
}

export interface GovernanceViolationItem {
  id: string;
  policy_id: string;
  rule_id: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  component: string;
  message: string;
  details?: Record<string, unknown>;
  status?: string;
}

export interface GovernanceResult {
  result_id: string;
  project_id: string;
  commit_id: string;
  compliance_score: number;
  total_violations: number;
  critical_violations: number;
  violations?: GovernanceViolationItem[];
  created_at?: string;
}

export async function listGovernancePolicies(): Promise<GovernancePolicy[]> {
  return apiClient<GovernancePolicy[]>("/api/v1/governance/policies");
}

export async function getGovernancePolicy(policyId: string): Promise<GovernancePolicy> {
  return apiClient<GovernancePolicy>(`/api/v1/governance/policy/${policyId}`);
}

export async function createGovernancePolicy(policy: GovernancePolicy): Promise<{ status: string; policy_id: string }> {
  return apiClient<{ status: string; policy_id: string }>("/api/v1/governance/policy", {
    method: "POST",
    body: JSON.stringify(policy),
  });
}

export async function updateGovernancePolicy(policy: GovernancePolicy): Promise<{ status: string; policy_id: string }> {
  return apiClient<{ status: string; policy_id: string }>("/api/v1/governance/policy", {
    method: "PUT",
    body: JSON.stringify(policy),
  });
}

export async function verifyGovernance(payload: GovernanceRequest): Promise<GovernanceResult> {
  return apiClient<GovernanceResult>("/api/v1/governance/verify", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getGovernanceResults(projectId: string): Promise<GovernanceResult[]> {
  return apiClient<GovernanceResult[]>(`/api/v1/governance/results/${projectId}`);
}

export async function getGovernanceResult(resultId: string): Promise<GovernanceResult> {
  return apiClient<GovernanceResult>(`/api/v1/governance/result/${resultId}`);
}

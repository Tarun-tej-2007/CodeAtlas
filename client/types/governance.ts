export interface GovernancePolicy {
  policy_id: string;
  name: string;
  description: string;
  rules: Array<Record<string, unknown>>;
  is_active: boolean;
}

export interface GovernanceViolation {
  violation_id: string;
  rule_id: string;
  severity: "critical" | "high" | "medium" | "low";
  source_component: string;
  target_component?: string;
  message: string;
}

export interface GovernanceResult {
  result_id: string;
  project_id: string;
  compliance_score: number;
  total_violations: number;
  critical_violations: number;
  violations: GovernanceViolation[];
  evaluated_at: string;
}

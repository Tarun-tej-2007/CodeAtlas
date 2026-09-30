import { ProjectResponse } from "./project";

export interface ArchitectureOverviewMetrics {
  healthScore: number;
  healthDeltaPercent: number;
  healthStatus: "Healthy" | "Warning" | "Critical";
  totalDependencies: number;
  dependenciesDelta: number;
  policyViolations: number;
  criticalPolicyViolations: number;
  architectureDrift: "Low" | "Medium" | "High";
  driftDeltaPercent: number;
}

export interface HealthTrendPoint {
  id: string;
  name: string;
  date: string;
  score: number;
  commitHash?: string;
}

export interface ArchitectureStatusCounts {
  components: number;
  services: number;
  modules: number;
  externalDependencies: number;
  healthyCount: number;
  warningCount: number;
  criticalCount: number;
}

export type IssueSeverity = "Critical" | "High" | "Medium" | "Low";

export interface NeedsAttentionItem {
  id: string;
  severity: IssueSeverity;
  title: string;
  explanation: string;
  affectedComponent: string;
  ruleCategory?: string;
}

export type ChangeType =
  | "Dependency added"
  | "Component modified"
  | "Architecture snapshot created"
  | "New module detected"
  | "Interface altered";

export interface ArchitectureChangeItem {
  id: string;
  type: ChangeType;
  identifier: string;
  timestamp: string;
  author?: string;
}

export type AIImpact = "High" | "Medium" | "Low";

export interface AIInsightItem {
  id: string;
  recommendation: string;
  explanation: string;
  evidence: string[];
  confidence: number;
  impact: AIImpact;
  actionLabel: string;
}

export interface DashboardData {
  lastAnalysisTimestamp: string;
  overview: ArchitectureOverviewMetrics;
  healthTrends: HealthTrendPoint[];
  healthStats: {
    current: number;
    previous: number;
    trend: number;
  };
  statusCounts: ArchitectureStatusCounts;
  attentionItems: NeedsAttentionItem[];
  recentChanges: ArchitectureChangeItem[];
  aiInsights: AIInsightItem[];
  recentProjects: ProjectResponse[];
}

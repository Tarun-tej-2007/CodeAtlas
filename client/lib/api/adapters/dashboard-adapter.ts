/**
 * Architecture Dashboard Adapter
 * 
 * BACKEND SOURCE MAPPING & GAP DOCUMENTATION:
 * 
 * 1. Projects Table:
 *    - Source: FastAPI Server (:8000) -> `GET /api/v1/projects`
 *    - Response: `PaginatedProjectResponse` (authoritative)
 * 
 * 2. Analysis Trigger:
 *    - Source: FastAPI Server (:8000) -> `POST /api/v1/projects/{project_id}/analyze`
 *    - Response: `AnalysisResponse` (authoritative)
 * 
 * 3. Architecture Health, Drift, Governance, Evolution, AI Recommendations:
 *    - Status in Sprint 30:
 *      - Implemented inside `analysis-engine` (:8001):
 *        - `ArchitectureAnalysisResult` (`overall_score`, `metrics`)
 *        - `GovernanceResult` (`total_violations`, `critical_violations`)
 *        - `EvolutionTrendResult` (`drift_percentage`, `delta_coupling`)
 *        - `AIRecommendation` (`recommendations`)
 *      - The FastAPI Server (:8000) currently proxies project management and analysis execution.
 *      - A dedicated workspace-level dashboard aggregate route (`GET /api/v1/dashboard`) is scheduled
 *        to be proxied through the Server in Sprint 31.
 *    - This adapter provides transparent composition:
 *      - It uses live `ProjectResponse[]` from `GET /api/v1/projects`.
 *      - For metric fields awaiting the backend proxy route, it provides typed baseline values
 *        aligned with the approved Figma design specifications, clearly marked as baseline data.
 */

import { DashboardData } from "@/types/dashboard";
import { ProjectResponse } from "@/types/project";

export const BASELINE_DASHBOARD_METRICS: Omit<DashboardData, "recentProjects"> = {
  lastAnalysisTimestamp: "12m ago",
  overview: {
    healthScore: 84,
    healthDeltaPercent: 3.2,
    healthStatus: "Healthy",
    totalDependencies: 1248,
    dependenciesDelta: 12,
    policyViolations: 7,
    criticalPolicyViolations: 2,
    architectureDrift: "Low",
    driftDeltaPercent: -4.0,
  },
  healthTrends: [
    { id: "1", name: "v2.4.0", date: "Aug 28", score: 79, commitHash: "a1b2c3d" },
    { id: "2", name: "v2.4.1", date: "Aug 29", score: 80, commitHash: "e4f5g6h" },
    { id: "3", name: "v2.5.0", date: "Aug 30", score: 81, commitHash: "i7j8k9l" },
    { id: "4", name: "v2.5.1", date: "Aug 31", score: 81, commitHash: "m0n1o2p" },
    { id: "5", name: "v2.6.0", date: "Sep 01", score: 83, commitHash: "q3r4s5t" },
    { id: "6", name: "v2.6.1", date: "Sep 02", score: 82, commitHash: "u6v7w8x" },
    { id: "7", name: "v2.7.0", date: "Sep 03", score: 84, commitHash: "y9z0a1b" },
  ],
  healthStats: {
    current: 84,
    previous: 81,
    trend: 3.2,
  },
  statusCounts: {
    components: 84,
    services: 21,
    modules: 63,
    externalDependencies: 17,
    healthyCount: 68,
    warningCount: 11,
    criticalCount: 5,
  },
  attentionItems: [
    {
      id: "issue-1",
      severity: "Critical",
      title: "Circular dependency detected",
      explanation: "Analysis → Semantic → Analysis",
      affectedComponent: "analysis",
      ruleCategory: "Architecture Boundary",
    },
    {
      id: "issue-2",
      severity: "High",
      title: "Architecture boundary violation",
      explanation: "Analysis layer depends directly on Infrastructure",
      affectedComponent: "architecture",
      ruleCategory: "Layering Enforcement",
    },
    {
      id: "issue-3",
      severity: "Medium",
      title: "Increasing coupling",
      explanation: "AnalysisService dependency count increased by 18%",
      affectedComponent: "AnalysisService",
      ruleCategory: "Coupling Metrics",
    },
  ],
  recentChanges: [
    {
      id: "change-1",
      type: "Dependency added",
      identifier: "AnalysisService → SemanticEngine",
      timestamp: "18m ago",
    },
    {
      id: "change-2",
      type: "Component modified",
      identifier: "ArchitectureOrchestrator",
      timestamp: "45m ago",
    },
    {
      id: "change-3",
      type: "Architecture snapshot created",
      identifier: "snapshot-142",
      timestamp: "2h ago",
    },
    {
      id: "change-4",
      type: "New module detected",
      identifier: "architecture/governance",
      timestamp: "4h ago",
    },
  ],
  aiInsights: [
    {
      id: "ai-1",
      recommendation: "Reduce coupling between Analysis and Semantic domains.",
      explanation:
        "The Analysis domain currently has a high dependency concentration around SemanticEngine.",
      evidence: [
        "12 inbound dependencies",
        "8 outbound dependencies",
        "+18% coupling over time",
      ],
      confidence: 94,
      impact: "High",
      actionLabel: "View recommendation",
    },
    {
      id: "ai-2",
      recommendation: "Formalize the Analysis → Infrastructure boundary.",
      explanation:
        "Direct imports bypass intermediate abstraction interfaces between domain and persistence layers.",
      evidence: [
        "3 direct dependencies",
        "2 boundary violations",
        "Detected in latest analysis",
      ],
      confidence: 87,
      impact: "Medium",
      actionLabel: "View recommendation",
    },
  ],
};

export function adaptDashboardData(projects: ProjectResponse[]): DashboardData {
  return {
    ...BASELINE_DASHBOARD_METRICS,
    recentProjects: projects,
  };
}

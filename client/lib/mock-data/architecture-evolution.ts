import { ArchitectureEvolutionData, EvolutionSnapshot, EvolutionEvent } from "@/types/architecture-evolution-ui";

const snapshots: EvolutionSnapshot[] = [
  { id: "snap-1", timestamp: "Sep 05", healthScore: 76, componentCount: 69, serviceCount: 17, moduleCount: 52, dependencyCount: 930, violationCount: 12, criticalViolationCount: 4, driftScore: 18, complexityScore: 45, couplingScore: 65, riskCounts: { Critical: 4, High: 8, Medium: 10, Low: 12 } },
  { id: "snap-2", timestamp: "Sep 10", healthScore: 79, componentCount: 73, serviceCount: 18, moduleCount: 55, dependencyCount: 1010, violationCount: 10, criticalViolationCount: 3, driftScore: 15, complexityScore: 48, couplingScore: 63, riskCounts: { Critical: 3, High: 7, Medium: 9, Low: 11 } },
  { id: "snap-3", timestamp: "Sep 14", healthScore: 81, componentCount: 76, serviceCount: 19, moduleCount: 57, dependencyCount: 1087, violationCount: 9, criticalViolationCount: 2, driftScore: 13, complexityScore: 50, couplingScore: 60, riskCounts: { Critical: 2, High: 6, Medium: 9, Low: 10 } },
  { id: "snap-4", timestamp: "Sep 18", healthScore: 80, componentCount: 78, serviceCount: 20, moduleCount: 59, dependencyCount: 1124, violationCount: 11, criticalViolationCount: 3, driftScore: 16, complexityScore: 52, couplingScore: 68, riskCounts: { Critical: 3, High: 7, Medium: 10, Low: 10 } },
  { id: "snap-5", timestamp: "Sep 21", healthScore: 82, componentCount: 80, serviceCount: 20, moduleCount: 60, dependencyCount: 1178, violationCount: 8, criticalViolationCount: 2, driftScore: 11, complexityScore: 54, couplingScore: 62, riskCounts: { Critical: 2, High: 5, Medium: 8, Low: 9 } },
  { id: "snap-6", timestamp: "Sep 24", healthScore: 81, componentCount: 82, serviceCount: 21, moduleCount: 61, dependencyCount: 1204, violationCount: 9, criticalViolationCount: 3, driftScore: 13, complexityScore: 55, couplingScore: 64, riskCounts: { Critical: 3, High: 5, Medium: 8, Low: 9 } },
  { id: "snap-7", timestamp: "Sep 27", healthScore: 83, componentCount: 83, serviceCount: 21, moduleCount: 62, dependencyCount: 1236, violationCount: 8, criticalViolationCount: 2, driftScore: 9, complexityScore: 58, couplingScore: 59, riskCounts: { Critical: 2, High: 4, Medium: 7, Low: 9 } },
  { id: "snap-8", timestamp: "Sep 29", healthScore: 84, componentCount: 84, serviceCount: 21, moduleCount: 63, dependencyCount: 1248, violationCount: 7, criticalViolationCount: 2, driftScore: 7, complexityScore: 59, couplingScore: 57, riskCounts: { Critical: 2, High: 3, Medium: 6, Low: 8 } },
  { id: "snap-9", timestamp: "Oct 01", healthScore: 84, componentCount: 84, serviceCount: 21, moduleCount: 63, dependencyCount: 1248, violationCount: 7, criticalViolationCount: 2, driftScore: 6, complexityScore: 59, couplingScore: 57, riskCounts: { Critical: 2, High: 3, Medium: 5, Low: 8 } },
];

const events: EvolutionEvent[] = [
  {
    id: "evt-1",
    timestamp: "Oct 01",
    title: "Architecture Health stabilized",
    description: "Minor dependency adjustments resulted in a stabilized architecture health score of 84.",
    category: "quality",
    severity: "Low",
    affectedComponents: [],
    changes: [
      { id: "c1", type: "architecture_drift", category: "quality", title: "Drift Reduced", description: "Drift reduced to 6%", timestamp: "Oct 01" }
    ]
  },
  {
    id: "evt-2",
    timestamp: "Sep 29",
    title: "ProjectService refactored",
    description: "Extracted responsibilities from ProjectService into new domain entities.",
    category: "structure",
    severity: "High",
    affectedComponents: ["ProjectService", "ProjectDomain"],
    changes: [
      { id: "c2", type: "component_modified", category: "structure", title: "ProjectService Refactored", description: "Split logic into domains", timestamp: "Sep 29" },
      { id: "c3", type: "violation_resolved", category: "quality", title: "Coupling Reduced", description: "Resolved high coupling in ProjectService", timestamp: "Sep 29" }
    ]
  },
  {
    id: "evt-3",
    timestamp: "Sep 27",
    title: "New ArchitectureService introduced",
    description: "A dedicated service was introduced to isolate architecture analysis orchestration.",
    category: "structure",
    severity: "Medium",
    affectedComponents: ["ArchitectureService", "ArchitectureController"],
    changes: [
      { id: "c4", type: "component_added", category: "structure", title: "ArchitectureService Added", description: "Added to Application Layer", timestamp: "Sep 27" },
      { id: "c5", type: "dependency_added", category: "dependency", title: "Controller Dependency", description: "Controller depends on new service", timestamp: "Sep 27" }
    ]
  },
  {
    id: "evt-4",
    timestamp: "Sep 24",
    title: "Circular dependency detected",
    description: "A new circular dependency was introduced between AnalysisService and GovernanceService.",
    category: "dependency",
    severity: "Critical",
    affectedComponents: ["AnalysisService", "GovernanceService"],
    changes: [
      { id: "c6", type: "violation_introduced", category: "dependency", title: "Circular Dependency", description: "Cycle detected", timestamp: "Sep 24", severity: "Critical" }
    ]
  },
  {
    id: "evt-5",
    timestamp: "Sep 21",
    title: "Boundary violation resolved",
    description: "Removed direct infrastructure access from Presentation layer.",
    category: "boundary",
    severity: "High",
    affectedComponents: ["DashboardController", "PostgreSQLRepository"],
    changes: [
      { id: "c7", type: "violation_resolved", category: "boundary", title: "Boundary Repaired", description: "Controller no longer bypasses Application", timestamp: "Sep 21" },
      { id: "c8", type: "dependency_removed", category: "dependency", title: "Direct DB Access Removed", description: "Removed infra dependency", timestamp: "Sep 21" }
    ]
  },
  {
    id: "evt-6",
    timestamp: "Sep 18",
    title: "RepositoryScanner added",
    description: "Introduced a new infrastructure adapter for parsing repositories.",
    category: "structure",
    severity: "Medium",
    affectedComponents: ["RepositoryScanner", "GitHubAdapter"],
    changes: [
      { id: "c9", type: "component_added", category: "structure", title: "RepositoryScanner Added", description: "Added to Infrastructure Layer", timestamp: "Sep 18" }
    ]
  }
];

export const MOCK_EVOLUTION_DATA: ArchitectureEvolutionData = {
  snapshots,
  events,
  stats: {
    totalChanges: 24,
    componentsAdded: 15,
    componentsRemoved: 2,
    dependenciesAdded: 318,
    dependenciesRemoved: 94,
    violationsIntroduced: 6,
    violationsResolved: 11,
    currentDrift: 6,
    healthChange: 8
  },
  driftBreakdown: {
    boundaryDrift: 3,
    dependencyDrift: 7,
    structuralDrift: 5,
    couplingDrift: 8
  }
};

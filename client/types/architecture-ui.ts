export type ArchitectureRiskLevel = "Low" | "Medium" | "High" | "Critical";
export type ArchitectureHealthLevel = "Healthy" | "Warning" | "Critical";

export interface ArchitectureOverview {
  healthScore: number;
  trend: number;
  componentCount: number;
  serviceCount: number;
  moduleCount: number;
  externalDependencyCount: number;
  violationCount: number;
  criticalViolationCount: number;
  lastAnalysis: string;
}

export interface ArchitectureComponent {
  id: string;
  name: string;
  type: string;
  layerId: string;
  path: string;
  description: string;
  dependencyCount: number;
  dependentCount: number;
  complexity: number;
  health: number;
  risk: ArchitectureRiskLevel;
  issueCount: number;
}

export interface ArchitectureLayer {
  id: string;
  name: string;
  description: string;
  order: number;
  components: ArchitectureComponent[];
}

export interface ArchitectureBoundary {
  id: string;
  sourceLayer: string;
  targetLayer: string;
  allowed: boolean;
  dependencyCount: number;
  violationCount: number;
}

export interface ArchitectureViolation {
  id: string;
  severity: ArchitectureRiskLevel;
  title: string;
  description: string;
  source: string;
  target: string;
  sourceLayer: string;
  targetLayer: string;
  rule: string;
  filePath: string;
  line: number;
}

export interface ArchitectureRisk {
  id: string;
  severity: ArchitectureRiskLevel;
  title: string;
  description: string;
  affectedComponents: string[];
}

export interface ArchitectureStats {
  components: number;
  services: number;
  modules: number;
  externalDependencies: number;
  boundaries: number;
  violations: number;
}

export interface ArchitectureHistoryEntry {
  id: string;
  timestamp: string;
  healthScore: number;
  componentCount: number;
  violationCount: number;
  status: string;
}

export interface ArchitectureHealthBreakdown {
  boundaryCompliance: number;
  dependencyHealth: number;
  modularity: number;
  coupling: number;
  architectureDrift: number;
  overall: number;
}

export interface ArchitectureData {
  overview: ArchitectureOverview;
  layers: ArchitectureLayer[];
  boundaries: ArchitectureBoundary[];
  violations: ArchitectureViolation[];
  risks: ArchitectureRisk[];
  stats: ArchitectureStats;
  history: ArchitectureHistoryEntry[];
  healthBreakdown: ArchitectureHealthBreakdown;
}

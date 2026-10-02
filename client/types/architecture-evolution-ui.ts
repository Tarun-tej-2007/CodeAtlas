export type EvolutionChangeType = 
  | "component_added" 
  | "component_removed" 
  | "dependency_added" 
  | "dependency_removed" 
  | "boundary_changed" 
  | "violation_introduced" 
  | "violation_resolved" 
  | "architecture_drift"
  | "component_modified";

export type EvolutionCategory = "structure" | "dependency" | "boundary" | "quality" | "risk";
export type EvolutionSeverity = "Critical" | "High" | "Medium" | "Low";

export interface EvolutionSnapshot {
  id: string;
  timestamp: string;
  healthScore: number;
  componentCount: number;
  serviceCount: number;
  moduleCount: number;
  dependencyCount: number;
  violationCount: number;
  criticalViolationCount: number;
  driftScore: number;
  complexityScore: number;
  couplingScore: number;
  riskCounts: {
    Critical: number;
    High: number;
    Medium: number;
    Low: number;
  };
}

export interface EvolutionChange {
  id: string;
  type: EvolutionChangeType;
  category: EvolutionCategory;
  title: string;
  description: string;
  timestamp: string;
  severity?: EvolutionSeverity;
  source?: string;
  target?: string;
  filePath?: string;
  affectedComponents?: string[];
}

export interface EvolutionEvent {
  id: string;
  timestamp: string;
  title: string;
  description: string;
  category: EvolutionCategory;
  severity?: EvolutionSeverity;
  affectedComponents: string[];
  changes: EvolutionChange[];
}

export interface ArchitectureTrendPoint {
  timestamp: string;
  health: number;
  drift: number;
  violations: number;
  complexity: number;
  coupling: number;
  components: number;
  dependencies: number;
}

export interface ArchitectureComparison {
  fromSnapshot: EvolutionSnapshot;
  toSnapshot: EvolutionSnapshot;
  addedComponents: string[];
  removedComponents: string[];
  addedDependencies: number;
  removedDependencies: number;
  newViolations: string[];
  resolvedViolations: string[];
  architectureChanges: EvolutionChange[];
}

export interface EvolutionStats {
  totalChanges: number;
  componentsAdded: number;
  componentsRemoved: number;
  dependenciesAdded: number;
  dependenciesRemoved: number;
  violationsIntroduced: number;
  violationsResolved: number;
  currentDrift: number;
  healthChange: number;
}

export interface EvolutionDriftBreakdown {
  boundaryDrift: number;
  dependencyDrift: number;
  structuralDrift: number;
  couplingDrift: number;
}

export interface ArchitectureEvolutionData {
  snapshots: EvolutionSnapshot[];
  events: EvolutionEvent[];
  stats: EvolutionStats;
  driftBreakdown: EvolutionDriftBreakdown;
}

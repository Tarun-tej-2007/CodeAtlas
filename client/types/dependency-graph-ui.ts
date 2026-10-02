export type DependencyLayer = "presentation" | "application" | "domain" | "infrastructure" | "external";
export type DependencyRelationship = "imports" | "calls" | "uses" | "extends" | "implements" | "depends_on";
export type DependencyRisk = "Low" | "Medium" | "High" | "Critical";

export interface DependencyNode {
  id: string;
  label: string;
  path: string;
  type: string;
  layer: DependencyLayer;
  language: string;
  dependencyCount: number;
  dependentCount: number;
  risk: DependencyRisk;
  complexity: number;
  issueCount: number;
}

export interface DependencyEdge {
  id: string;
  source: string;
  target: string;
  relationship: DependencyRelationship;
  weight: number;
  isCircular?: boolean;
}

export interface DependencyGraphData {
  nodes: DependencyNode[];
  edges: DependencyEdge[];
}

export interface DependencyGraphStats {
  totalNodes: number;
  totalEdges: number;
  internalDependencies: number;
  externalDependencies: number;
  circularDependencies: number;
  averageDependencies: number;
  highestCouplingNode: string;
}

export interface DependencyIssue {
  id: string;
  type: string;
  severity: DependencyRisk;
  title: string;
  description: string;
  affectedNodes: string[];
}

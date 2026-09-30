export interface ArchitectureChange {
  change_id: string;
  change_type: string;
  component_id: string;
  description: string;
  timestamp: string;
}

export interface EvolutionTrendResult {
  evolution_id: string;
  drift_percentage: number;
  delta_coupling: number;
  risk_level: "low" | "medium" | "high";
  evaluated_at: string;
}

export interface EvolutionResult {
  evolution_id: string;
  changes: ArchitectureChange[];
  summary: Record<string, unknown>;
}

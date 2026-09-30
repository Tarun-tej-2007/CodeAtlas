export interface AIRecommendation {
  title: string;
  description: string;
  category: string;
  priority: "critical" | "high" | "medium" | "low";
  affected_files?: string[];
  affected_components?: string[];
  confidence_score: number;
  reasoning?: string;
  suggested_actions?: string[];
}

export interface ArchitectureReview {
  review_id: string;
  project_id: string;
  commit_id: string;
  summary: string;
  recommendations: AIRecommendation[];
  created_at: string;
}

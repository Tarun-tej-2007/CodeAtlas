export type ActivityType = 
  | "ANALYSIS" 
  | "ARCHITECTURE" 
  | "DEPENDENCY" 
  | "GOVERNANCE" 
  | "AI_REVIEW" 
  | "DECISION" 
  | "REPORT" 
  | "SETTINGS" 
  | "PROJECT" 
  | "SYSTEM";

export type ActivitySeverity = "INFO" | "SUCCESS" | "WARNING" | "CRITICAL";

export type ActivityStatus = "COMPLETED" | "IN_PROGRESS" | "FAILED" | "RESOLVED" | "UPDATED";

export type ActorType = "USER" | "SYSTEM" | "AI" | "AUTOMATION";

export interface ActivityMetadata {
  durationStr?: string;
  filesAnalyzed?: number;
  findingsCount?: number;
  architectureScore?: number;
  governanceCompliance?: number;
  recommendationsCount?: number;
  resolutionTime?: string;
  [key: string]: unknown;
}

export interface ActivityEvent {
  id: string;
  title: string;
  description: string;
  timestamp: string; // ISO or readable string, we'll use deterministic timestamps
  dateLabel: string; // E.g., "Today", "Yesterday", "Sep 30"
  type: ActivityType;
  severity: ActivitySeverity;
  status: ActivityStatus;
  actor: {
    name: string;
    type: ActorType;
  };
  relatedProject?: string;
  relatedComponent?: string;
  relatedModule?: string;
  metadata?: ActivityMetadata;
}

export interface ActivityFilterState {
  search: string;
  type: ActivityType | "ALL";
  severity: ActivitySeverity | "ALL";
  status: ActivityStatus | "ALL";
  actorType: ActorType | "ALL";
  date: "ALL" | "TODAY" | "YESTERDAY" | "LAST_7_DAYS" | "LAST_30_DAYS";
}

export interface ActivityStats {
  total: number;
  today: number;
  warnings: number;
  critical: number;
  resolved: number;
  automated: number;
}

export interface ActivitySummary {
  description: string;
  highlights: string[];
}

export interface ActivityTimelineGroup {
  dateLabel: string;
  events: ActivityEvent[];
}


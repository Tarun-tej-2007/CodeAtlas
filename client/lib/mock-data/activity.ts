import { ActivityEvent } from "@/types/activity-ui";

export const MOCK_ACTIVITY_EVENTS: ActivityEvent[] = [
  // Today (8 events)
  {
    id: "act-01",
    title: "Comprehensive Architecture Review completed",
    description: "AI-assisted architecture review completed for Core Services. Found 1 critical boundary violation.",
    timestamp: "2 mins ago",
    dateLabel: "Today",
    type: "AI_REVIEW",
    severity: "WARNING",
    status: "COMPLETED",
    actor: { name: "System", type: "SYSTEM" },
    relatedProject: "Core Services",
    metadata: {
      architectureScore: 86,
      findingsCount: 14,
      recommendationsCount: 9,
      durationStr: "42 seconds"
    }
  },
  {
    id: "act-02",
    title: "Governance compliance evaluation completed",
    description: "Evaluated 12 active policies. Architecture Layering policy compliance is at 91%.",
    timestamp: "18 mins ago",
    dateLabel: "Today",
    type: "GOVERNANCE",
    severity: "INFO",
    status: "COMPLETED",
    actor: { name: "Automation", type: "AUTOMATION" },
    metadata: { governanceCompliance: 91, findingsCount: 3 }
  },
  {
    id: "act-03",
    title: "Dependency Graph analysis completed",
    description: "Scanned all workspaces. Identified 2 new circular dependencies in payment-gateway.",
    timestamp: "1 hour ago",
    dateLabel: "Today",
    type: "DEPENDENCY",
    severity: "WARNING",
    status: "COMPLETED",
    actor: { name: "System", type: "SYSTEM" },
    relatedComponent: "payment-gateway",
    metadata: { filesAnalyzed: 1284, findingsCount: 2 }
  },
  {
    id: "act-04",
    title: "Architecture recommendation marked as reviewed",
    description: "Decision to extract authentication logic from order-service was approved.",
    timestamp: "3 hours ago",
    dateLabel: "Today",
    type: "DECISION",
    severity: "SUCCESS",
    status: "RESOLVED",
    actor: { name: "Sarah Chen", type: "USER" },
    relatedProject: "order-service"
  },
  {
    id: "act-05",
    title: "Weekly Engineering Report generated",
    description: "PDF report generated containing the latest metrics.",
    timestamp: "4 hours ago",
    dateLabel: "Today",
    type: "REPORT",
    severity: "INFO",
    status: "COMPLETED",
    actor: { name: "System", type: "SYSTEM" }
  },
  {
    id: "act-06",
    title: "Critical architecture boundary violation detected",
    description: "UI components directly accessing database models.",
    timestamp: "5 hours ago",
    dateLabel: "Today",
    type: "ARCHITECTURE",
    severity: "CRITICAL",
    status: "FAILED",
    actor: { name: "Automation", type: "AUTOMATION" },
    metadata: { findingsCount: 1 }
  },
  {
    id: "act-07",
    title: "Incremental Analysis started",
    description: "Triggered by a webhook push to main branch.",
    timestamp: "6 hours ago",
    dateLabel: "Today",
    type: "ANALYSIS",
    severity: "INFO",
    status: "IN_PROGRESS",
    actor: { name: "System", type: "SYSTEM" }
  },
  {
    id: "act-08",
    title: "Architecture Settings updated",
    description: "Complexity threshold reduced from 20 to 15.",
    timestamp: "7 hours ago",
    dateLabel: "Today",
    type: "SETTINGS",
    severity: "INFO",
    status: "UPDATED",
    actor: { name: "Alex Kumar", type: "USER" }
  },

  // Yesterday (10 events)
  {
    id: "act-09",
    title: "Repository analysis completed",
    description: "Full scan completed successfully.",
    timestamp: "Yesterday, 09:12 AM",
    dateLabel: "Yesterday",
    type: "ANALYSIS",
    severity: "SUCCESS",
    status: "COMPLETED",
    actor: { name: "Automation", type: "AUTOMATION" },
    metadata: { durationStr: "3m 45s", filesAnalyzed: 8540 }
  },
  {
    id: "act-10",
    title: "Architecture boundary violation resolved",
    description: "Removed direct dependency between billing and user-profile.",
    timestamp: "Yesterday, 10:30 AM",
    dateLabel: "Yesterday",
    type: "ARCHITECTURE",
    severity: "SUCCESS",
    status: "RESOLVED",
    actor: { name: "Elena Rostova", type: "USER" },
    relatedComponent: "billing"
  },
  {
    id: "act-11",
    title: "Governance policy updated",
    description: "'Require Exception for Violations' was enabled.",
    timestamp: "Yesterday, 11:15 AM",
    dateLabel: "Yesterday",
    type: "GOVERNANCE",
    severity: "INFO",
    status: "UPDATED",
    actor: { name: "Marcus Webb", type: "USER" }
  },
  {
    id: "act-12",
    title: "Workspace settings updated",
    description: "Changed Default Analysis Depth to DEEP.",
    timestamp: "Yesterday, 11:45 AM",
    dateLabel: "Yesterday",
    type: "SETTINGS",
    severity: "INFO",
    status: "UPDATED",
    actor: { name: "Marcus Webb", type: "USER" }
  },
  {
    id: "act-13",
    title: "Project analysis started",
    description: "Initial scan for the newly added 'Analytics Data Pipeline' project.",
    timestamp: "Yesterday, 01:20 PM",
    dateLabel: "Yesterday",
    type: "PROJECT",
    severity: "INFO",
    status: "IN_PROGRESS",
    actor: { name: "System", type: "SYSTEM" },
    relatedProject: "Analytics Data Pipeline"
  },
  {
    id: "act-14",
    title: "Dependency Security check failed",
    description: "High severity CVE found in left-pad dependency.",
    timestamp: "Yesterday, 02:10 PM",
    dateLabel: "Yesterday",
    type: "DEPENDENCY",
    severity: "WARNING",
    status: "FAILED",
    actor: { name: "Automation", type: "AUTOMATION" },
    metadata: { findingsCount: 1 }
  },
  {
    id: "act-15",
    title: "Vulnerability resolved",
    description: "left-pad dependency was updated to a secure version.",
    timestamp: "Yesterday, 03:00 PM",
    dateLabel: "Yesterday",
    type: "DEPENDENCY",
    severity: "SUCCESS",
    status: "RESOLVED",
    actor: { name: "Sarah Chen", type: "USER" }
  },
  {
    id: "act-16",
    title: "Technical Debt report generated",
    description: "Generated on-demand report for Q3 planning.",
    timestamp: "Yesterday, 04:30 PM",
    dateLabel: "Yesterday",
    type: "REPORT",
    severity: "INFO",
    status: "COMPLETED",
    actor: { name: "Elena Rostova", type: "USER" }
  },
  {
    id: "act-17",
    title: "AI Architecture Review completed",
    description: "Reviewed the proposed microservice split.",
    timestamp: "Yesterday, 05:45 PM",
    dateLabel: "Yesterday",
    type: "AI_REVIEW",
    severity: "INFO",
    status: "COMPLETED",
    actor: { name: "AI", type: "AI" },
    metadata: { architectureScore: 92, recommendationsCount: 3 }
  },
  {
    id: "act-18",
    title: "System Maintenance",
    description: "Nightly database index rebuilt successfully.",
    timestamp: "Yesterday, 11:59 PM",
    dateLabel: "Yesterday",
    type: "SYSTEM",
    severity: "INFO",
    status: "COMPLETED",
    actor: { name: "System", type: "SYSTEM" }
  }
];

// Generate 24 more deterministic mock events for older dates
const OLD_DATES = ["Sep 30", "Sep 29", "Sep 28", "Sep 25", "Sep 20"];

let oldEventId = 19;
OLD_DATES.forEach((dateStr, index) => {
  // Generate a few events per date
  const eventsCount = index === 0 ? 6 : index === 1 ? 5 : index === 2 ? 5 : 4;
  
  for (let i = 0; i < eventsCount; i++) {
    const isAutomated = (oldEventId % 3 === 0);
    const isResolved = (oldEventId % 5 === 0);
    const isWarning = (oldEventId % 7 === 0);
    
    let type: ActivityEvent["type"] = "ANALYSIS";
    if (oldEventId % 2 === 0) type = "ARCHITECTURE";
    else if (oldEventId % 3 === 0) type = "GOVERNANCE";
    else if (oldEventId % 4 === 0) type = "REPORT";
    else if (oldEventId % 5 === 0) type = "DECISION";
    else if (oldEventId % 7 === 0) type = "PROJECT";
    
    let severity: ActivityEvent["severity"] = "INFO";
    if (isWarning) severity = "WARNING";
    else if (isResolved) severity = "SUCCESS";
    
    let status: ActivityEvent["status"] = "COMPLETED";
    if (isResolved) status = "RESOLVED";
    
    MOCK_ACTIVITY_EVENTS.push({
      id: `act-${oldEventId}`,
      title: isResolved ? "Issue resolved" : `${type.toLowerCase()} activity recorded`,
      description: `Deterministic historical event ${oldEventId} for CodeAtlas.`,
      timestamp: `${dateStr}, 10:00 AM`,
      dateLabel: dateStr,
      type,
      severity,
      status,
      actor: { 
        name: isAutomated ? "Automation" : "System", 
        type: isAutomated ? "AUTOMATION" : "SYSTEM" 
      }
    });
    
    oldEventId++;
  }
});


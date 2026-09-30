import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ArchitectureOverview } from "@/components/dashboard/architecture-overview";
import { ArchitectureStatus } from "@/components/dashboard/architecture-status";
import { NeedsAttention } from "@/components/dashboard/needs-attention";
import { ArchitectureChanges } from "@/components/dashboard/architecture-changes";
import { AIInsights } from "@/components/dashboard/ai-insights";
import { RecentProjects } from "@/components/dashboard/recent-projects";
import { DashboardSkeleton } from "@/components/dashboard/dashboard-skeleton";
import { DashboardError } from "@/components/dashboard/dashboard-error";
import { BASELINE_DASHBOARD_METRICS } from "@/lib/api/adapters/dashboard-adapter";

describe("Dashboard Metric Components", () => {
  it("renders ArchitectureOverview metrics correctly", () => {
    render(<ArchitectureOverview metrics={BASELINE_DASHBOARD_METRICS.overview} />);

    expect(screen.getByText("Architecture Health")).toBeInTheDocument();
    expect(screen.getByText("84")).toBeInTheDocument();
    expect(screen.getByText("Healthy")).toBeInTheDocument();
    expect(screen.getByText("+3.2%")).toBeInTheDocument();

    expect(screen.getByText("Dependencies")).toBeInTheDocument();
    expect(screen.getByText("1,248")).toBeInTheDocument();
    expect(screen.getByText("+12")).toBeInTheDocument();

    expect(screen.getByText("Policy Violations")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("2 critical")).toBeInTheDocument();

    expect(screen.getByText("Architecture Drift")).toBeInTheDocument();
    expect(screen.getByText("Low")).toBeInTheDocument();
  });

  it("renders ArchitectureStatus entity counts and distribution", () => {
    render(<ArchitectureStatus status={BASELINE_DASHBOARD_METRICS.statusCounts} />);

    expect(screen.getByText("Architecture Status")).toBeInTheDocument();
    expect(screen.getByText("84")).toBeInTheDocument(); // Components
    expect(screen.getByText("21")).toBeInTheDocument(); // Services
    expect(screen.getByText("63")).toBeInTheDocument(); // Modules
    expect(screen.getByText("17")).toBeInTheDocument(); // External Deps

    expect(screen.getByText("68")).toBeInTheDocument(); // Healthy
    expect(screen.getByText("11")).toBeInTheDocument(); // Warning
    expect(screen.getByText("5")).toBeInTheDocument(); // Critical
  });

  it("renders NeedsAttention violations with severity badges", () => {
    render(<NeedsAttention items={BASELINE_DASHBOARD_METRICS.attentionItems} />);

    expect(screen.getByText("Needs Attention")).toBeInTheDocument();
    expect(screen.getByText("Circular dependency detected")).toBeInTheDocument();
    expect(screen.getByText("Analysis → Semantic → Analysis")).toBeInTheDocument();
    expect(screen.getByText("analysis")).toBeInTheDocument();

    expect(screen.getByText("Architecture boundary violation")).toBeInTheDocument();
    expect(screen.getByText("architecture")).toBeInTheDocument();

    expect(screen.getByText("Increasing coupling")).toBeInTheDocument();
    expect(screen.getByText("AnalysisService")).toBeInTheDocument();
  });

  it("renders ArchitectureChanges chronological activity log", () => {
    render(<ArchitectureChanges changes={BASELINE_DASHBOARD_METRICS.recentChanges} />);

    expect(screen.getByText("Recent Architecture Changes")).toBeInTheDocument();
    expect(screen.getByText("Dependency added")).toBeInTheDocument();
    expect(screen.getByText("AnalysisService → SemanticEngine")).toBeInTheDocument();
    expect(screen.getByText("Component modified")).toBeInTheDocument();
    expect(screen.getByText("ArchitectureOrchestrator")).toBeInTheDocument();
  });

  it("renders AIInsights analytical recommendations with evidence and confidence", () => {
    render(<AIInsights insights={BASELINE_DASHBOARD_METRICS.aiInsights} />);

    expect(screen.getByText("AI Architecture Insights")).toBeInTheDocument();
    expect(
      screen.getByText("Reduce coupling between Analysis and Semantic domains.")
    ).toBeInTheDocument();
    expect(screen.getByText("94% Confidence")).toBeInTheDocument();
    expect(screen.getByText("High Impact")).toBeInTheDocument();
    expect(screen.getByText("12 inbound dependencies")).toBeInTheDocument();
    expect(screen.getByText("8 outbound dependencies")).toBeInTheDocument();
  });

  it("renders RecentProjects table with project health scores", () => {
    render(<RecentProjects projects={[]} />);

    expect(screen.getByText("Recent Projects")).toBeInTheDocument();
    expect(screen.getByText("CodeAtlas")).toBeInTheDocument();
    expect(screen.getByText("SatQuery")).toBeInTheDocument();
    expect(screen.getByText("Agridata Copilot")).toBeInTheDocument();
  });

  it("renders DashboardSkeleton loading state", () => {
    render(<DashboardSkeleton />);
    expect(screen.getByTestId("dashboard-skeleton")).toBeInTheDocument();
  });

  it("renders DashboardError with retry action", () => {
    const onRetry = () => {};
    render(<DashboardError message="Network timeout" onRetry={onRetry} />);

    expect(screen.getByTestId("dashboard-error")).toBeInTheDocument();
    expect(screen.getByText("Network timeout")).toBeInTheDocument();
    expect(screen.getByText("Retry connection")).toBeInTheDocument();
  });
});

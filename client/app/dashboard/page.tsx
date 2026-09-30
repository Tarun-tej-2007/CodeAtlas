"use client";

import { AppShell } from "@/components/layout/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { ArchitectureOverview } from "@/components/dashboard/architecture-overview";
import { ArchitectureHealth } from "@/components/dashboard/architecture-health";
import { ArchitectureStatus } from "@/components/dashboard/architecture-status";
import { NeedsAttention } from "@/components/dashboard/needs-attention";
import { ArchitectureChanges } from "@/components/dashboard/architecture-changes";
import { AIInsights } from "@/components/dashboard/ai-insights";
import { RecentProjects } from "@/components/dashboard/recent-projects";
import { DashboardSkeleton } from "@/components/dashboard/dashboard-skeleton";
import { DashboardError } from "@/components/dashboard/dashboard-error";
import { useDashboardData } from "@/lib/query/use-dashboard";

export default function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useDashboardData();

  return (
    <AppShell breadcrumb="Dashboard">
      <div className="space-y-4.5">
        {isLoading && <DashboardSkeleton />}

        {isError && (
          <DashboardError
            message={error instanceof Error ? error.message : "Failed to load dashboard data."}
            onRetry={() => refetch()}
          />
        )}

        {data && !isLoading && (
          <>
            {/* 1. Header with Title & Analysis Trigger */}
            <DashboardHeader
              lastAnalysisTimestamp={data.lastAnalysisTimestamp}
              projects={data.recentProjects}
              onAnalysisTriggered={() => refetch()}
            />

            {/* 2. Top Metric (Unified Architecture Overview Surface) */}
            <ArchitectureOverview metrics={data.overview} />

            {/* 3. Health Trend & Architecture Status Row */}
            <div className="grid grid-cols-1 gap-4.5 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <ArchitectureHealth
                  trendData={data.healthTrends}
                  stats={data.healthStats}
                />
              </div>
              <div className="lg:col-span-1">
                <ArchitectureStatus status={data.statusCounts} />
              </div>
            </div>

            {/* 4. Needs Attention & Recent Changes Row */}
            <div className="grid grid-cols-1 gap-4.5 lg:grid-cols-2">
              <NeedsAttention items={data.attentionItems} />
              <ArchitectureChanges changes={data.recentChanges} />
            </div>

            {/* 5. AI Architecture Insights */}
            <AIInsights insights={data.aiInsights} />

            {/* 6. Recent Projects Table */}
            <RecentProjects projects={data.recentProjects} />
          </>
        )}
      </div>
    </AppShell>
  );
}

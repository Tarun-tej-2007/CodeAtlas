"use client";

import { Activity, GitFork, ShieldAlert, GitCompareArrows } from "lucide-react";
import { ArchitectureOverviewMetrics } from "@/types/dashboard";
import { formatNumber, formatPercentage } from "@/lib/utils";

interface ArchitectureOverviewProps {
  metrics: ArchitectureOverviewMetrics;
}

export function ArchitectureOverview({ metrics }: ArchitectureOverviewProps) {
  return (
    <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] shadow-xs overflow-hidden">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 divide-y sm:divide-y-0 divide-[#1E293B] sm:divide-x">
        {/* 1. Architecture Health (Visually Dominant - 4 cols on lg) */}
        <div className="p-4 sm:p-5 lg:col-span-4 flex flex-col justify-between relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#3B82F6]/10 text-[#3B82F6]">
                <Activity className="h-3.5 w-3.5" />
              </div>
              <span className="text-xs font-semibold text-[#F8FAFC]">
                Architecture Health
              </span>
            </div>
            <span className="inline-flex items-center rounded-full bg-[#22C55E]/10 border border-[#22C55E]/20 px-2 py-0.5 text-[11px] font-medium text-[#22C55E]">
              {metrics.healthStatus}
            </span>
          </div>

          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-[#F8FAFC] font-mono">
              {metrics.healthScore}
            </span>
            <span className="text-sm text-[#64748B] font-mono">/ 100</span>
          </div>

          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#94A3B8]">
            <span className="font-mono text-[#22C55E]">
              {formatPercentage(metrics.healthDeltaPercent)}
            </span>
            <span>from previous analysis</span>
          </div>
        </div>

        {/* 2. Dependencies (3 cols on lg) */}
        <div className="p-4 sm:p-5 lg:col-span-3 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#141E2E] text-[#94A3B8]">
                <GitFork className="h-3.5 w-3.5" />
              </div>
              <span className="text-xs font-medium text-[#94A3B8]">
                Dependencies
              </span>
            </div>
          </div>

          <div className="mt-3">
            <span className="text-2xl font-semibold tracking-tight text-[#F8FAFC] font-mono">
              {formatNumber(metrics.totalDependencies)}
            </span>
          </div>

          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#94A3B8]">
            <span className="font-mono text-[#CBD5E1]">
              +{metrics.dependenciesDelta}
            </span>
            <span>since previous analysis</span>
          </div>
        </div>

        {/* 3. Policy Violations (3 cols on lg) */}
        <div className="p-4 sm:p-5 lg:col-span-3 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#EF4444]/10 text-[#EF4444]">
                <ShieldAlert className="h-3.5 w-3.5" />
              </div>
              <span className="text-xs font-medium text-[#94A3B8]">
                Policy Violations
              </span>
            </div>
            {metrics.criticalPolicyViolations > 0 && (
              <span className="inline-flex items-center rounded bg-[#EF4444]/10 px-1.5 py-0.5 text-[10px] font-medium text-[#EF4444] border border-[#EF4444]/20 font-mono">
                {metrics.criticalPolicyViolations} critical
              </span>
            )}
          </div>

          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-semibold tracking-tight text-[#F8FAFC] font-mono">
              {metrics.policyViolations}
            </span>
          </div>

          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#94A3B8]">
            <span>
              {metrics.criticalPolicyViolations > 0
                ? `${metrics.criticalPolicyViolations} require urgent resolution`
                : "All non-critical"}
            </span>
          </div>
        </div>

        {/* 4. Architecture Drift (2 cols on lg) */}
        <div className="p-4 sm:p-5 lg:col-span-2 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#141E2E] text-[#94A3B8]">
                <GitCompareArrows className="h-3.5 w-3.5" />
              </div>
              <span className="text-xs font-medium text-[#94A3B8]">
                Architecture Drift
              </span>
            </div>
          </div>

          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-semibold tracking-tight text-[#F8FAFC] font-mono">
              {metrics.architectureDrift}
            </span>
          </div>

          <div className="mt-2 flex items-center gap-1.5 text-xs text-[#94A3B8]">
            <span className="font-mono text-[#22C55E]">
              {metrics.driftDeltaPercent}%
            </span>
            <span>from previous analysis</span>
          </div>
        </div>
      </div>
    </div>
  );
}

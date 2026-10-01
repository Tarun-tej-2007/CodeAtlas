"use client";

import { AnalysisMetrics } from "@/types/analysis-ui";
import { FileCode, AlertTriangle, ShieldAlert, Copy, CheckCircle2, Activity } from "lucide-react";
import { formatNumber } from "@/lib/utils";

interface AnalysisMetricsGridProps {
  metrics: AnalysisMetrics;
}

export function AnalysisMetricsGrid({ metrics }: AnalysisMetricsGridProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
      {/* Files */}
      <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4 flex flex-col justify-between shadow-xs">
        <div className="flex items-center gap-2 text-[#94A3B8]">
          <FileCode className="h-4 w-4" />
          <span className="text-xs font-medium uppercase tracking-wider">Files</span>
        </div>
        <div className="mt-3">
          <span className="text-2xl font-semibold text-[#F8FAFC] font-mono">{formatNumber(metrics.totalFiles)}</span>
        </div>
      </div>

      {/* Lines of Code */}
      <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4 flex flex-col justify-between shadow-xs">
        <div className="flex items-center gap-2 text-[#94A3B8]">
          <Activity className="h-4 w-4" />
          <span className="text-xs font-medium uppercase tracking-wider">Lines of Code</span>
        </div>
        <div className="mt-3">
          <span className="text-2xl font-semibold text-[#F8FAFC] font-mono">{formatNumber(metrics.linesOfCode)}</span>
        </div>
      </div>

      {/* Technical Debt */}
      <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4 flex flex-col justify-between shadow-xs">
        <div className="flex items-center justify-between text-[#94A3B8]">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            <span className="text-xs font-medium uppercase tracking-wider">Tech Debt</span>
          </div>
          {metrics.technicalDebtRatio > 5 ? (
            <span className="flex h-2 w-2 rounded-full bg-[#EAB308]" />
          ) : (
            <span className="flex h-2 w-2 rounded-full bg-[#22C55E]" />
          )}
        </div>
        <div className="mt-3 flex items-baseline gap-1">
          <span className="text-2xl font-semibold text-[#F8FAFC] font-mono">{metrics.technicalDebtRatio}</span>
          <span className="text-sm text-[#94A3B8]">%</span>
        </div>
      </div>

      {/* Issues */}
      <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4 flex flex-col justify-between shadow-xs relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-4">
           {metrics.issues > 0 && <div className="h-8 w-8 rounded-full bg-[#EF4444]/10 blur-xl"></div>}
        </div>
        <div className="flex items-center gap-2 text-[#94A3B8]">
          <ShieldAlert className="h-4 w-4 text-[#EF4444]" />
          <span className="text-xs font-medium uppercase tracking-wider">Issues</span>
        </div>
        <div className="mt-3">
          <span className="text-2xl font-semibold text-[#EF4444] font-mono">{metrics.issues}</span>
        </div>
      </div>

      {/* Code Smells */}
      <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4 flex flex-col justify-between shadow-xs">
        <div className="flex items-center gap-2 text-[#94A3B8]">
          <AlertTriangle className="h-4 w-4 text-[#EAB308]" />
          <span className="text-xs font-medium uppercase tracking-wider">Smells</span>
        </div>
        <div className="mt-3">
          <span className="text-2xl font-semibold text-[#F8FAFC] font-mono">{metrics.codeSmells}</span>
        </div>
      </div>

      {/* Duplication & Coverage */}
      <div className="rounded-lg border border-[#1E293B] bg-[#0F1726] p-4 flex flex-col justify-between shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[#94A3B8]">
            <Copy className="h-3.5 w-3.5" />
            <span className="text-xs font-medium">Duplicated</span>
          </div>
          <span className="text-sm font-mono text-[#F8FAFC]">{metrics.duplicatedLines}%</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[#94A3B8]">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span className="text-xs font-medium">Coverage</span>
          </div>
          <span className="text-sm font-mono text-[#22C55E]">{metrics.testCoverage}%</span>
        </div>
      </div>
    </div>
  );
}

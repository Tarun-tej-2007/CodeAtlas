"use client";

import { ArchitectureOverview as ArchOverview } from "@/types/architecture-ui";
import { Play } from "lucide-react";

interface ArchitectureHeaderProps {
  overview: ArchOverview;
  isAnalyzing: boolean;
  onRunAnalysis: () => void;
}

export function ArchitectureHeader({ overview, isAnalyzing, onRunAnalysis }: ArchitectureHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <div>
        <h1 className="text-2xl font-semibold text-[#F8FAFC]">Architecture</h1>
        <p className="text-sm text-[#94A3B8] mt-1">
          Understand your system structure, boundaries, and architectural health.
        </p>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex flex-col items-end">
          <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Architecture Health</span>
          <div className="flex items-center gap-2">
            <span className="text-lg text-[#F8FAFC] font-semibold">{overview.healthScore} <span className="text-sm text-[#64748B]">/ 100</span></span>
            <span className="text-xs text-[#22C55E] bg-[#22C55E]/10 px-1.5 py-0.5 rounded border border-[#22C55E]/20">
              +{overview.trend}%
            </span>
          </div>
        </div>
        
        <div className="h-8 w-px bg-[#1E293B] hidden sm:block"></div>

        <div className="flex flex-col items-end">
          <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Last analysis</span>
          <span className="text-sm text-[#94A3B8] mt-0.5">{overview.lastAnalysis}</span>
        </div>

        <button
          onClick={onRunAnalysis}
          disabled={isAnalyzing}
          className="flex items-center gap-2 rounded-md bg-[#3B82F6] px-4 py-2 text-sm font-medium text-white hover:bg-[#2563EB] disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:ring-offset-2 focus:ring-offset-[#080D18]"
        >
          {isAnalyzing ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Running...
            </>
          ) : (
            <>
              <Play className="h-4 w-4" fill="currentColor" />
              Run Analysis
            </>
          )}
        </button>
      </div>
    </div>
  );
}

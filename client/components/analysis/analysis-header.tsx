"use client";

import { Play, Clock, CheckCircle2, Loader2 } from "lucide-react";

interface AnalysisHeaderProps {
  status: "idle" | "running" | "completed";
  onRunAnalysis: () => void;
  lastAnalysisTimestamp: string;
}

export function AnalysisHeader({ status, onRunAnalysis, lastAnalysisTimestamp }: AnalysisHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 className="text-2xl font-semibold text-[#F8FAFC]">Repository Analysis</h1>
        <p className="text-sm text-[#94A3B8] mt-1">Deep static and semantic analysis of your codebase.</p>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="flex items-center gap-6 mr-2">
          <div className="flex flex-col">
            <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Repository</span>
            <span className="text-sm text-[#F8FAFC] font-medium">CodeAtlas</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Branch</span>
            <span className="text-sm text-[#F8FAFC] font-mono">main</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold">Last Analysis</span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <Clock className="h-3 w-3 text-[#94A3B8]" />
              <span className="text-sm text-[#94A3B8] font-mono">{lastAnalysisTimestamp}</span>
            </div>
          </div>
        </div>

        <div className="h-8 w-px bg-[#1E293B] hidden sm:block"></div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 mr-2">
            {status === "completed" && <CheckCircle2 className="h-4 w-4 text-[#22C55E]" />}
            {status === "running" && <Loader2 className="h-4 w-4 text-[#3B82F6] animate-spin" />}
            {status === "idle" && <div className="h-2 w-2 rounded-full bg-[#94A3B8] ml-1 mr-1" />}
            <span className="text-sm font-medium text-[#CBD5E1]">
              {status === "completed" ? "Analysis Complete" : status === "running" ? "Analyzing..." : "Ready"}
            </span>
          </div>

          <button
            onClick={onRunAnalysis}
            disabled={status === "running"}
            className="flex items-center gap-2 rounded-md bg-[#3B82F6] px-4 py-2 text-sm font-medium text-white hover:bg-[#2563EB] transition-colors focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:ring-offset-2 focus:ring-offset-[#080D18] disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {status === "running" ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            Run Analysis
          </button>
        </div>
      </div>
    </div>
  );
}

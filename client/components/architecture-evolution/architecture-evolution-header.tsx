import { useState } from "react";
import { Play, Clock, ArrowUpRight, Activity } from "lucide-react";

interface ArchitectureEvolutionHeaderProps {
  healthScore: number;
  driftScore: number;
  isAnalyzing?: boolean;
  onRunAnalysis?: () => void;
}

export function ArchitectureEvolutionHeader({
  healthScore,
  driftScore,
  isAnalyzing,
  onRunAnalysis,
}: ArchitectureEvolutionHeaderProps) {
  const getDriftLabel = (drift: number) => {
    if (drift < 10) return "Low";
    if (drift < 20) return "Medium";
    return "High";
  };

  const getDriftColor = (drift: number) => {
    if (drift < 10) return "text-[#22C55E]";
    if (drift < 20) return "text-[#F59E0B]";
    return "text-[#EF4444]";
  };

  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
      <div>
        <h1 className="text-2xl font-semibold text-[#F8FAFC]">Architecture Evolution</h1>
        <p className="text-[#94A3B8] text-sm mt-1">
          Track structural changes, architectural drift, and system health across analysis history.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-4 bg-[#0F1726] border border-[#1E293B] rounded-lg px-4 py-2">
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase font-semibold">Current Health</span>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#3B82F6]" />
              <span className="text-sm font-medium text-[#F8FAFC]">{healthScore} / 100</span>
            </div>
          </div>
          <div className="w-px h-8 bg-[#1E293B]" />
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase font-semibold">Architecture Drift</span>
            <div className="flex items-center gap-2">
              <ArrowUpRight className={`w-4 h-4 ${getDriftColor(driftScore)}`} />
              <span className={`text-sm font-medium ${getDriftColor(driftScore)}`}>{getDriftLabel(driftScore)}</span>
            </div>
          </div>
          <div className="w-px h-8 bg-[#1E293B]" />
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase font-semibold">Last Analysis</span>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#94A3B8]" />
              <span className="text-sm font-medium text-[#F8FAFC]">12 mins ago</span>
            </div>
          </div>
        </div>

        <button
          onClick={onRunAnalysis}
          disabled={isAnalyzing}
          className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed h-[50px]"
        >
          {isAnalyzing ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          <span>{isAnalyzing ? "Analyzing..." : "Run Analysis"}</span>
        </button>
      </div>
    </div>
  );
}

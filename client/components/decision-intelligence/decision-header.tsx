import { RefreshCw } from "lucide-react";
import { DecisionHealth } from "@/types/decision-intelligence-ui";

interface DecisionHeaderProps {
  health: DecisionHealth;
  lastAnalysis: string;
  onRunAnalysis: () => void;
  isRunning: boolean;
}

export function DecisionHeader({ health, lastAnalysis, onRunAnalysis, isRunning }: DecisionHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-[#F8FAFC]">Decision Intelligence</h1>
        <p className="text-sm text-[#94A3B8] mt-1">
          Turn architectural signals into actionable engineering decisions.
        </p>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="hidden sm:flex flex-col items-end mr-2">
          <div className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Decision Health</div>
          <div className="text-lg font-bold text-[#F8FAFC]">{health.score} <span className="text-sm text-[#94A3B8] font-normal">/ 100</span></div>
        </div>
        <div className="hidden sm:flex flex-col items-end mr-2">
          <div className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Last Analysis</div>
          <div className="text-sm font-medium text-[#F8FAFC]">{lastAnalysis}</div>
        </div>
        
        <button
          onClick={onRunAnalysis}
          disabled={isRunning}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-[#3B82F6] px-4 py-2 text-sm font-medium text-white shadow hover:bg-[#2563EB] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#3B82F6] disabled:pointer-events-none disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${isRunning ? "animate-spin" : ""}`} />
          {isRunning ? "Running..." : "Run Decision Analysis"}
        </button>
      </div>
    </div>
  );
}

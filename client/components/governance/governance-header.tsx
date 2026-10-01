import { Play, Settings, ShieldCheck, Clock } from "lucide-react";

interface GovernanceHeaderProps {
  healthScore: number;
  lastEvaluated: string;
  isEvaluating: boolean;
  onRunCheck: () => void;
  onOpenSettings: () => void;
}

export function GovernanceHeader({ healthScore, lastEvaluated, isEvaluating, onRunCheck, onOpenSettings }: GovernanceHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
      <div>
        <h1 className="text-2xl font-semibold text-[#F8FAFC]">Governance</h1>
        <p className="text-[#94A3B8] text-sm mt-1">
          Monitor architectural policies, engineering standards, and compliance across your codebase.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-4 bg-[#0F1726] border border-[#1E293B] rounded-lg px-4 py-2">
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase font-semibold">Governance Health</span>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#3B82F6]" />
              <span className="text-sm font-medium text-[#F8FAFC]">{healthScore} / 100</span>
            </div>
          </div>
          <div className="w-px h-8 bg-[#1E293B]" />
          <div className="flex flex-col">
            <span className="text-xs text-[#64748B] uppercase font-semibold">Last Evaluation</span>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#94A3B8]" />
              <span className="text-sm font-medium text-[#F8FAFC]">{lastEvaluated}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onRunCheck}
            disabled={isEvaluating}
            className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed h-[50px]"
          >
            {isEvaluating ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{isEvaluating ? "Running Check..." : "Run Compliance Check"}</span>
          </button>
          
          <button
            onClick={onOpenSettings}
            className="flex items-center justify-center w-[50px] h-[50px] bg-[#0F1726] hover:bg-[#1E293B] border border-[#1E293B] text-[#94A3B8] hover:text-[#F8FAFC] rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

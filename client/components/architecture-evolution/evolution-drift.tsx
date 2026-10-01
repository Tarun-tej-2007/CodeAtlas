import { EvolutionDriftBreakdown } from "@/types/architecture-evolution-ui";

interface EvolutionDriftProps {
  currentDrift: number;
  breakdown: EvolutionDriftBreakdown;
}

export function EvolutionDrift({ currentDrift, breakdown }: EvolutionDriftProps) {
  const getDriftColor = (val: number) => {
    if (val < 5) return "bg-[#22C55E]";
    if (val < 10) return "bg-[#F59E0B]";
    return "bg-[#EF4444]";
  };

  const getDriftTextColor = (val: number) => {
    if (val < 10) return "text-[#22C55E]";
    if (val < 20) return "text-[#F59E0B]";
    return "text-[#EF4444]";
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 h-full flex flex-col">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4">Architecture Drift</h2>
      
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-[#1E293B]/50">
        <span className="text-sm text-[#94A3B8]">Current Drift</span>
        <div className="flex items-center gap-2">
          <span className={`text-xl font-semibold ${getDriftTextColor(currentDrift)}`}>{currentDrift}%</span>
          <span className={`text-xs px-2 py-0.5 rounded-full bg-[#1E293B] ${getDriftTextColor(currentDrift)}`}>
            {currentDrift < 10 ? "Low" : currentDrift < 20 ? "Medium" : "High"}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-4 flex-1">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Boundary Drift</span>
            <span className="text-[#F8FAFC]">{breakdown.boundaryDrift}%</span>
          </div>
          <div className="h-1.5 bg-[#080D18] rounded-full overflow-hidden">
            <div className={`h-full ${getDriftColor(breakdown.boundaryDrift)}`} style={{ width: `${Math.min(100, breakdown.boundaryDrift * 3)}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Dependency Drift</span>
            <span className="text-[#F8FAFC]">{breakdown.dependencyDrift}%</span>
          </div>
          <div className="h-1.5 bg-[#080D18] rounded-full overflow-hidden">
            <div className={`h-full ${getDriftColor(breakdown.dependencyDrift)}`} style={{ width: `${Math.min(100, breakdown.dependencyDrift * 3)}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Structural Drift</span>
            <span className="text-[#F8FAFC]">{breakdown.structuralDrift}%</span>
          </div>
          <div className="h-1.5 bg-[#080D18] rounded-full overflow-hidden">
            <div className={`h-full ${getDriftColor(breakdown.structuralDrift)}`} style={{ width: `${Math.min(100, breakdown.structuralDrift * 3)}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-[#94A3B8]">Coupling Drift</span>
            <span className="text-[#F8FAFC]">{breakdown.couplingDrift}%</span>
          </div>
          <div className="h-1.5 bg-[#080D18] rounded-full overflow-hidden">
            <div className={`h-full ${getDriftColor(breakdown.couplingDrift)}`} style={{ width: `${Math.min(100, breakdown.couplingDrift * 3)}%` }} />
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-3 border-t border-[#1E293B]/50">
        <p className="text-xs text-[#64748B] italic">
          Drift measures how much the current architecture differs from the selected baseline.
        </p>
      </div>
    </div>
  );
}

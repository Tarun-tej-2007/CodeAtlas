import { EvolutionSnapshot } from "@/types/architecture-evolution-ui";
import { ArrowRight, PlusCircle, MinusCircle, ShieldAlert, CheckCircle2 } from "lucide-react";

interface EvolutionComparisonProps {
  baselineSnapshot: EvolutionSnapshot;
  currentSnapshot: EvolutionSnapshot;
}

export function EvolutionComparison({ baselineSnapshot, currentSnapshot }: EvolutionComparisonProps) {
  const getDiffColor = (from: number, to: number, invert = false) => {
    if (from === to) return "text-[#94A3B8]";
    const positive = to > from;
    const isGood = invert ? !positive : positive;
    return isGood ? "text-[#22C55E]" : "text-[#EF4444]";
  };

  const renderMetric = (label: string, from: number, to: number, invert = false) => (
    <div className="flex items-center justify-between py-2 border-b border-[#1E293B]/50 last:border-0">
      <span className="text-sm text-[#94A3B8] w-32">{label}</span>
      <div className="flex items-center gap-3 flex-1 justify-end">
        <span className="text-sm font-medium text-[#F8FAFC]">{from}</span>
        <ArrowRight className="w-3 h-3 text-[#64748B]" />
        <span className={`text-sm font-semibold ${getDiffColor(from, to, invert)}`}>{to}</span>
      </div>
    </div>
  );

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-[#F8FAFC]">Before / After Comparison</h2>
        <div className="flex items-center gap-2 bg-[#080D18] rounded-md border border-[#1E293B] px-3 py-1">
          <span className="text-xs font-medium text-[#94A3B8]">{baselineSnapshot.timestamp}</span>
          <ArrowRight className="w-3 h-3 text-[#64748B]" />
          <span className="text-xs font-medium text-[#F8FAFC]">{currentSnapshot.timestamp}</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 flex flex-col gap-6">
        <div>
          <h3 className="text-xs font-semibold text-[#64748B] uppercase mb-2">Metrics</h3>
          <div className="bg-[#080D18] rounded-md border border-[#1E293B] px-3 py-1">
            {renderMetric("Health", baselineSnapshot.healthScore, currentSnapshot.healthScore)}
            {renderMetric("Components", baselineSnapshot.componentCount, currentSnapshot.componentCount)}
            {renderMetric("Services", baselineSnapshot.serviceCount, currentSnapshot.serviceCount)}
            {renderMetric("Modules", baselineSnapshot.moduleCount, currentSnapshot.moduleCount)}
            {renderMetric("Dependencies", baselineSnapshot.dependencyCount, currentSnapshot.dependencyCount)}
            {renderMetric("Violations", baselineSnapshot.violationCount, currentSnapshot.violationCount, true)}
            {renderMetric("Drift", baselineSnapshot.driftScore, currentSnapshot.driftScore, true)}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <h3 className="text-xs font-semibold text-[#22C55E] uppercase mb-2 flex items-center gap-1">
              <PlusCircle className="w-3 h-3" /> Added Components
            </h3>
            <div className="bg-[#080D18] rounded-md border border-[#1E293B] p-2 flex flex-col gap-1 min-h-[60px]">
              <span className="text-xs text-[#CBD5E1]">ArchitectureService</span>
              <span className="text-xs text-[#CBD5E1]">DecisionService</span>
              <span className="text-xs text-[#CBD5E1]">RepositoryScanner</span>
            </div>
          </div>
          <div>
            <h3 className="text-xs font-semibold text-[#EF4444] uppercase mb-2 flex items-center gap-1">
              <MinusCircle className="w-3 h-3" /> Removed Components
            </h3>
            <div className="bg-[#080D18] rounded-md border border-[#1E293B] p-2 flex flex-col gap-1 min-h-[60px]">
              <span className="text-xs text-[#CBD5E1]">LegacyAnalyzer</span>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <h3 className="text-xs font-semibold text-[#22C55E] uppercase mb-2 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Resolved Violations
            </h3>
            <div className="bg-[#080D18] rounded-md border border-[#1E293B] p-2 flex flex-col gap-1 min-h-[60px]">
              <span className="text-xs text-[#CBD5E1] truncate" title="Direct DB Access Removed">Direct DB Access Removed</span>
              <span className="text-xs text-[#CBD5E1] truncate" title="Coupling Reduced in ProjectService">Coupling Reduced in ProjectService</span>
            </div>
          </div>
          <div>
            <h3 className="text-xs font-semibold text-[#F59E0B] uppercase mb-2 flex items-center gap-1">
              <ShieldAlert className="w-3 h-3" /> New Violations
            </h3>
            <div className="bg-[#080D18] rounded-md border border-[#1E293B] p-2 flex flex-col gap-1 min-h-[60px]">
              <span className="text-xs text-[#CBD5E1] truncate" title="Circular Dependency: Analysis <-> Gov">Circular Dependency: Analysis &lt;-&gt; Gov</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

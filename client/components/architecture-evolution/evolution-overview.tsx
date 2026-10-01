import { EvolutionStats } from "@/types/architecture-evolution-ui";
import { TrendingUp, TrendingDown, Package, Link2, AlertTriangle, ArrowUpRight, CheckCircle } from "lucide-react";

interface EvolutionOverviewProps {
  stats: EvolutionStats;
}

export function EvolutionOverview({ stats }: EvolutionOverviewProps) {
  const isHealthPositive = stats.healthChange >= 0;
  const netComponents = stats.componentsAdded - stats.componentsRemoved;
  const netDependencies = stats.dependenciesAdded - stats.dependenciesRemoved;
  const netViolations = stats.violationsIntroduced - stats.violationsResolved;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          {isHealthPositive ? <TrendingUp className="w-4 h-4 text-[#22C55E]" /> : <TrendingDown className="w-4 h-4 text-[#EF4444]" />}
          <span className="text-xs uppercase font-semibold">Health Change</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {stats.healthChange > 0 ? "+" : ""}{stats.healthChange}
        </div>
        <div className="text-xs text-[#64748B] mt-1">from previous baseline</div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <Package className="w-4 h-4" />
          <span className="text-xs uppercase font-semibold">Components</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {netComponents > 0 ? "+" : ""}{netComponents}
        </div>
        <div className="text-xs text-[#64748B] mt-1">since first snapshot</div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <Link2 className="w-4 h-4" />
          <span className="text-xs uppercase font-semibold">Dependencies</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {netDependencies > 0 ? "+" : ""}{netDependencies}
        </div>
        <div className="text-xs text-[#64748B] mt-1">since first snapshot</div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          {netViolations <= 0 ? <CheckCircle className="w-4 h-4 text-[#22C55E]" /> : <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />}
          <span className="text-xs uppercase font-semibold">Violations</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {netViolations > 0 ? "+" : ""}{netViolations}
        </div>
        <div className="text-xs text-[#64748B] mt-1">resolved net</div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <ArrowUpRight className="w-4 h-4" />
          <span className="text-xs uppercase font-semibold">Arch. Drift</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {stats.currentDrift}%
        </div>
        <div className="text-xs text-[#64748B] mt-1">Current</div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <TrendingUp className="w-4 h-4" />
          <span className="text-xs uppercase font-semibold">Significant Changes</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {stats.totalChanges}
        </div>
        <div className="text-xs text-[#64748B] mt-1">recorded events</div>
      </div>
    </div>
  );
}

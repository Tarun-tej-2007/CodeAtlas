import { EvolutionStats } from "@/types/architecture-evolution-ui";
import { Package, Link2, AlertTriangle, Layers, Maximize } from "lucide-react";

interface EvolutionChangeSummaryProps {
  stats: EvolutionStats;
}

export function EvolutionChangeSummary({ stats }: EvolutionChangeSummaryProps) {
  // Using some mock logic for services/modules based on components
  const servicesAdded = Math.floor(stats.componentsAdded * 0.25);
  const servicesRemoved = 0;
  const modulesAdded = Math.floor(stats.componentsAdded * 0.75);
  const modulesRemoved = stats.componentsRemoved;

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 h-full">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4">Change Summary</h2>
      
      <div className="flex flex-col gap-3">
        <div className="flex justify-between items-center py-2 border-b border-[#1E293B]/50">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <Package className="w-4 h-4" />
            <span className="text-sm">Components</span>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium">
            <span className="text-[#22C55E]">+{stats.componentsAdded} added</span>
            <span className="text-[#64748B]">/</span>
            <span className="text-[#EF4444]">-{stats.componentsRemoved} removed</span>
          </div>
        </div>

        <div className="flex justify-between items-center py-2 border-b border-[#1E293B]/50">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <Link2 className="w-4 h-4" />
            <span className="text-sm">Dependencies</span>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium">
            <span className="text-[#22C55E]">+{stats.dependenciesAdded} added</span>
            <span className="text-[#64748B]">/</span>
            <span className="text-[#EF4444]">-{stats.dependenciesRemoved} removed</span>
          </div>
        </div>

        <div className="flex justify-between items-center py-2 border-b border-[#1E293B]/50">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm">Violations</span>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium">
            <span className="text-[#EF4444]">+{stats.violationsIntroduced} intro</span>
            <span className="text-[#64748B]">/</span>
            <span className="text-[#22C55E]">-{stats.violationsResolved} rslvd</span>
          </div>
        </div>

        <div className="flex justify-between items-center py-2 border-b border-[#1E293B]/50">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <Layers className="w-4 h-4" />
            <span className="text-sm">Services</span>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium">
            <span className="text-[#22C55E]">+{servicesAdded} added</span>
            <span className="text-[#64748B]">/</span>
            <span className="text-[#EF4444]">-{servicesRemoved} removed</span>
          </div>
        </div>

        <div className="flex justify-between items-center py-2">
          <div className="flex items-center gap-2 text-[#94A3B8]">
            <Maximize className="w-4 h-4" />
            <span className="text-sm">Modules</span>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium">
            <span className="text-[#22C55E]">+{modulesAdded} added</span>
            <span className="text-[#64748B]">/</span>
            <span className="text-[#EF4444]">-{modulesRemoved} removed</span>
          </div>
        </div>
      </div>
    </div>
  );
}

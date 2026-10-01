"use client";

import { ArchitectureComponent, ArchitectureData } from "@/types/architecture-ui";
import { X, ExternalLink, Activity, Target, Network } from "lucide-react";
import Link from "next/link";

interface ArchitectureComponentDetailsProps {
  componentId: string;
  data: ArchitectureData;
  onClose: () => void;
}

export function ArchitectureComponentDetails({ componentId, data, onClose }: ArchitectureComponentDetailsProps) {
  const component = data.layers
    .flatMap(l => l.components)
    .find(c => c.id === componentId);

  if (!component) return null;

  const layer = data.layers.find(l => l.id === component.layerId);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "Critical": return "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20";
      case "High": return "text-[#F97316] bg-[#F97316]/10 border-[#F97316]/20";
      case "Medium": return "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20";
      default: return "text-[#22C55E] bg-[#22C55E]/10 border-[#22C55E]/20";
    }
  };

  return (
    <div className="w-80 h-full bg-[#0F1726] border-l border-[#1E293B] flex flex-col shadow-xl z-20">
      <div className="p-4 border-b border-[#1E293B] flex items-center justify-between sticky top-0 bg-[#0F1726]">
        <h2 className="font-semibold text-[#F8FAFC]">Component Details</h2>
        <button onClick={onClose} className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-4 overflow-y-auto custom-scrollbar flex-1">
        <div className="mb-6">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-lg font-bold text-[#F8FAFC] break-all">{component.name}</h3>
            <span className={`shrink-0 text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded border ${getRiskColor(component.risk)}`}>
              {component.risk}
            </span>
          </div>
          <p className="text-sm text-[#94A3B8] mt-1">{component.type}</p>
        </div>

        <div className="mb-6 space-y-4">
          <div>
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Path</span>
            <p className="text-sm text-[#E2E8F0] font-mono mt-1 break-all bg-[#141E2E] p-2 rounded border border-[#1E293B]">
              {component.path}
            </p>
          </div>
          <div>
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Layer</span>
            <p className="text-sm text-[#E2E8F0] mt-1">{layer?.name}</p>
          </div>
          <div>
            <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold">Description</span>
            <p className="text-sm text-[#E2E8F0] mt-1">{component.description}</p>
          </div>
        </div>

        <div className="mb-6">
          <span className="text-xs text-[#64748B] uppercase tracking-wider font-semibold mb-3 block">Statistics</span>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#141E2E] rounded border border-[#1E293B] p-3">
              <div className="flex items-center gap-1.5 text-[#94A3B8] mb-1">
                <Network className="h-3 w-3" />
                <span className="text-xs">Dependencies</span>
              </div>
              <span className="text-lg font-semibold text-[#F8FAFC]">{component.dependencyCount}</span>
            </div>
            <div className="bg-[#141E2E] rounded border border-[#1E293B] p-3">
              <div className="flex items-center gap-1.5 text-[#94A3B8] mb-1">
                <Target className="h-3 w-3" />
                <span className="text-xs">Dependents</span>
              </div>
              <span className="text-lg font-semibold text-[#F8FAFC]">{component.dependentCount}</span>
            </div>
            <div className="bg-[#141E2E] rounded border border-[#1E293B] p-3">
              <div className="flex items-center gap-1.5 text-[#94A3B8] mb-1">
                <Activity className="h-3 w-3" />
                <span className="text-xs">Complexity</span>
              </div>
              <span className="text-lg font-semibold text-[#F8FAFC]">{component.complexity}</span>
            </div>
            <div className="bg-[#141E2E] rounded border border-[#1E293B] p-3">
              <div className="flex items-center gap-1.5 text-[#94A3B8] mb-1">
                <span className="text-xs">Health</span>
              </div>
              <span className="text-lg font-semibold text-[#F8FAFC]">{component.health}</span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <button className="w-full bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium py-2 rounded transition-colors flex items-center justify-center gap-2 border border-[#334155]">
            Focus Component
          </button>
          <Link 
            href="/graph" 
            className="w-full bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium py-2 rounded transition-colors flex items-center justify-center gap-2 border border-[#334155]"
          >
            View Dependencies <ExternalLink className="h-3 w-3" />
          </Link>
          {component.issueCount > 0 && (
            <button className="w-full bg-[#EF4444]/10 hover:bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/20 text-sm font-medium py-2 rounded transition-colors flex items-center justify-center gap-2">
              View Violations
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

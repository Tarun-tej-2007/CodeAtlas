"use client";

import { DependencyLayer, DependencyRelationship, DependencyRisk } from "@/types/dependency-graph-ui";
import { Filter } from "lucide-react";

export interface GraphFilters {
  layer: DependencyLayer | "All";
  relationship: DependencyRelationship | "All";
  risk: DependencyRisk | "All";
  issues: "All" | "Has Issues" | "No Issues";
}

interface DependencyFilterPanelProps {
  filters: GraphFilters;
  onFilterChange: (filters: GraphFilters) => void;
  onClear: () => void;
}

export function DependencyFilterPanel({ filters, onFilterChange, onClear }: DependencyFilterPanelProps) {
  const updateFilter = (key: keyof GraphFilters, value: string) => {
    onFilterChange({ ...filters, [key]: value });
  };

  return (
    <div className="w-full flex flex-col h-full overflow-y-auto custom-scrollbar">
      <div className="p-4 border-b border-[#1E293B] flex items-center justify-between sticky top-0 bg-[#0F1726] z-10">
        <div className="flex items-center gap-2 text-[#F8FAFC]">
          <Filter className="h-4 w-4" />
          <h3 className="text-sm font-semibold">Filters</h3>
        </div>
        <button onClick={onClear} className="text-[10px] uppercase font-bold text-[#3B82F6] hover:text-[#60A5FA]">
          Clear
        </button>
      </div>

      <div className="p-4 space-y-6">
        <div>
          <label className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider block mb-2">Layer</label>
          <select 
            value={filters.layer} 
            onChange={(e) => updateFilter("layer", e.target.value)}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md py-1.5 px-3 text-sm text-[#CBD5E1] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] appearance-none"
          >
            <option value="All">All Layers</option>
            <option value="presentation">Presentation</option>
            <option value="application">Application</option>
            <option value="domain">Domain</option>
            <option value="infrastructure">Infrastructure</option>
            <option value="external">External</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider block mb-2">Relationship</label>
          <select 
            value={filters.relationship} 
            onChange={(e) => updateFilter("relationship", e.target.value)}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md py-1.5 px-3 text-sm text-[#CBD5E1] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] appearance-none"
          >
            <option value="All">All Types</option>
            <option value="imports">Imports</option>
            <option value="calls">Calls</option>
            <option value="uses">Uses</option>
            <option value="extends">Extends</option>
            <option value="implements">Implements</option>
            <option value="depends_on">Depends On</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider block mb-2">Risk</label>
          <select 
            value={filters.risk} 
            onChange={(e) => updateFilter("risk", e.target.value)}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md py-1.5 px-3 text-sm text-[#CBD5E1] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] appearance-none"
          >
            <option value="All">All Risks</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider block mb-2">Issues</label>
          <select 
            value={filters.issues} 
            onChange={(e) => updateFilter("issues", e.target.value)}
            className="w-full bg-[#080D18] border border-[#1E293B] rounded-md py-1.5 px-3 text-sm text-[#CBD5E1] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] appearance-none"
          >
            <option value="All">All</option>
            <option value="Has Issues">Has Issues</option>
            <option value="No Issues">No Issues</option>
          </select>
        </div>
      </div>
    </div>
  );
}

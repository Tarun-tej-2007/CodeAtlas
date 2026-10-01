"use client";

import { Search, Layers, Layout, Filter, AlertTriangle } from "lucide-react";

export type ViewMode = "overview" | "layers" | "boundaries" | "violations";

interface ArchitectureToolbarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
}

export function ArchitectureToolbar({
  searchQuery,
  onSearchChange,
  viewMode,
  onViewModeChange,
}: ArchitectureToolbarProps) {
  const modes = [
    { id: "overview", label: "Overview", icon: Layout },
    { id: "layers", label: "Layers", icon: Layers },
    { id: "boundaries", label: "Boundaries", icon: Filter },
    { id: "violations", label: "Violations", icon: AlertTriangle },
  ] as const;

  return (
    <div className="flex flex-col sm:flex-row gap-3 mb-4 items-center justify-between">
      <div className="relative w-full sm:w-64">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-[#64748B]" />
        </div>
        <input
          type="text"
          placeholder="Search components..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-[#1E293B] rounded-md leading-5 bg-[#0F1726] text-[#E2E8F0] placeholder-[#64748B] focus:outline-none focus:ring-1 focus:ring-[#3B82F6] focus:border-[#3B82F6] sm:text-sm transition-colors"
        />
      </div>

      <div className="flex bg-[#0F1726] p-1 rounded-md border border-[#1E293B] w-full sm:w-auto overflow-x-auto">
        {modes.map((mode) => {
          const Icon = mode.icon;
          const isActive = viewMode === mode.id;
          return (
            <button
              key={mode.id}
              onClick={() => onViewModeChange(mode.id)}
              className={`flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-sm whitespace-nowrap transition-colors ${
                isActive 
                  ? "bg-[#1E293B] text-[#F8FAFC] shadow-xs" 
                  : "text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#1E293B]/50"
              }`}
            >
              <Icon className="h-4 w-4" />
              {mode.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

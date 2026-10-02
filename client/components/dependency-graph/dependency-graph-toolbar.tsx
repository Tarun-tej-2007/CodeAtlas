"use client";

import { Search, Maximize, ZoomIn, ZoomOut, RotateCcw } from "lucide-react";

interface DependencyGraphToolbarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  layout: "hierarchical" | "force" | "circular";
  onLayoutChange: (layout: "hierarchical" | "force" | "circular") => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onReset: () => void;
}

export function DependencyGraphToolbar({
  searchQuery,
  onSearchChange,
  layout,
  onLayoutChange,
  onZoomIn,
  onZoomOut,
  onFitView,
  onReset,
}: DependencyGraphToolbarProps) {
  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 border-b border-[#1E293B] bg-[#0F1726]">
      <div className="relative w-full sm:w-64">
        <Search className="absolute left-2.5 top-2 h-4 w-4 text-[#64748B]" />
        <input
          type="text"
          placeholder="Search components..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full bg-[#080D18] border border-[#1E293B] rounded-md py-1.5 pl-8 pr-3 text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:ring-1 focus:ring-[#3B82F6]"
        />
      </div>

      <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
        <div className="flex items-center gap-1 bg-[#080D18] border border-[#1E293B] rounded-md p-1 mr-2">
          {(["hierarchical", "force", "circular"] as const).map((l) => (
            <button
              key={l}
              onClick={() => onLayoutChange(l)}
              className={`px-3 py-1 text-xs font-medium rounded-sm capitalize transition-colors ${
                layout === l ? "bg-[#1E293B] text-[#F8FAFC]" : "text-[#94A3B8] hover:text-[#CBD5E1]"
              }`}
            >
              {l}
            </button>
          ))}
        </div>

        <div className="h-6 w-px bg-[#1E293B] hidden sm:block mx-1"></div>

        <div className="flex items-center gap-1">
          <button onClick={onZoomIn} className="p-1.5 rounded-md text-[#94A3B8] hover:bg-[#1E293B] hover:text-[#F8FAFC]" title="Zoom In">
            <ZoomIn className="h-4 w-4" />
          </button>
          <button onClick={onZoomOut} className="p-1.5 rounded-md text-[#94A3B8] hover:bg-[#1E293B] hover:text-[#F8FAFC]" title="Zoom Out">
            <ZoomOut className="h-4 w-4" />
          </button>
          <button onClick={onFitView} className="p-1.5 rounded-md text-[#94A3B8] hover:bg-[#1E293B] hover:text-[#F8FAFC]" title="Fit View">
            <Maximize className="h-4 w-4" />
          </button>
          <button onClick={onReset} className="p-1.5 rounded-md text-[#94A3B8] hover:bg-[#1E293B] hover:text-[#F8FAFC]" title="Reset View">
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

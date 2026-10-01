import { Search, Filter, X } from "lucide-react";

interface EvolutionFiltersProps {
  categoryFilter: string;
  onCategoryFilterChange: (cat: string) => void;
  severityFilter: string;
  onSeverityFilterChange: (sev: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
}

export function EvolutionFilters({
  categoryFilter,
  onCategoryFilterChange,
  severityFilter,
  onSeverityFilterChange,
  searchQuery,
  onSearchChange
}: EvolutionFiltersProps) {
  const categories = ["All", "Structure", "Dependency", "Boundary", "Quality", "Risk"];
  const severities = ["All", "Critical", "High", "Medium", "Low"];

  const hasActiveFilters = categoryFilter !== "All" || severityFilter !== "All" || searchQuery;

  const clearFilters = () => {
    onCategoryFilterChange("All");
    onSeverityFilterChange("All");
    onSearchChange("");
  };

  return (
    <div className="flex flex-col gap-4 bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-[#94A3B8]" />
          <h2 className="text-sm font-semibold text-[#F8FAFC]">Filter Changes</h2>
        </div>
        {hasActiveFilters && (
          <button 
            onClick={clearFilters}
            className="text-xs text-[#94A3B8] hover:text-[#F8FAFC] flex items-center gap-1 transition-colors"
          >
            <X className="w-3 h-3" /> Clear
          </button>
        )}
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search events..."
            className="w-full pl-9 pr-4 py-1.5 bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:border-[#3B82F6]"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-[#64748B] uppercase font-semibold">Category</span>
          <select
            value={categoryFilter}
            onChange={(e) => onCategoryFilterChange(e.target.value)}
            className="bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1.5 focus:outline-none focus:border-[#3B82F6]"
          >
            {categories.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-[#64748B] uppercase font-semibold">Severity</span>
          <select
            value={severityFilter}
            onChange={(e) => onSeverityFilterChange(e.target.value)}
            className="bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1.5 focus:outline-none focus:border-[#3B82F6]"
          >
            {severities.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

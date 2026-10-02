import { ReportFilterState, ReportType, ReportStatus, ReportFormat } from "@/types/reports-ui";
import { Search } from "lucide-react";

interface ReportFiltersProps {
  filters: ReportFilterState;
  onFilterChange: (filters: Partial<ReportFilterState>) => void;
}

export function ReportFilters({ filters, onFilterChange }: ReportFiltersProps) {
  return (
    <div className="flex flex-col gap-4 p-4 bg-[#0F1726] border border-[#1E293B] rounded-lg mb-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
        <input
          type="text"
          placeholder="Search reports by title, description, or content..."
          value={filters.search}
          onChange={(e) => onFilterChange({ search: e.target.value })}
          className="w-full pl-9 pr-4 py-2 bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:border-[#3B82F6]"
        />
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <select
          value={filters.type}
          onChange={(e) => onFilterChange({ type: e.target.value as ReportType | "ALL" })}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Types</option>
          <option value="COMPREHENSIVE">Comprehensive</option>
          <option value="REPOSITORY_ANALYSIS">Repository Analysis</option>
          <option value="ARCHITECTURE">Architecture</option>
          <option value="DEPENDENCY">Dependency</option>
          <option value="GOVERNANCE">Governance</option>
          <option value="EVOLUTION">Evolution</option>
          <option value="DECISION">Decision</option>
          <option value="AI_ARCHITECTURE">AI Architecture</option>
        </select>
        
        <select
          value={filters.status}
          onChange={(e) => onFilterChange({ status: e.target.value as ReportStatus | "ALL" })}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Statuses</option>
          <option value="READY">Ready</option>
          <option value="GENERATING">Generating</option>
          <option value="COMPLETED">Completed</option>
          <option value="FAILED">Failed</option>
          <option value="SCHEDULED">Scheduled</option>
        </select>
        
        <select
          value={filters.format}
          onChange={(e) => onFilterChange({ format: e.target.value as ReportFormat | "ALL" })}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Formats</option>
          <option value="PDF">PDF</option>
          <option value="HTML">HTML</option>
          <option value="JSON">JSON</option>
        </select>
        
        <select
          value={filters.dateRange}
          onChange={(e) => onFilterChange({ dateRange: e.target.value as ReportFilterState["dateRange"] })}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Time</option>
          <option value="TODAY">Today</option>
          <option value="LAST_7_DAYS">Last 7 Days</option>
          <option value="LAST_30_DAYS">Last 30 Days</option>
        </select>
      </div>
    </div>
  );
}

import { Search } from "lucide-react";

interface ReviewFindingFiltersProps {
  searchQuery: string;
  setSearchQuery: (s: string) => void;
  severityFilter: string;
  setSeverityFilter: (s: string) => void;
  categoryFilter: string;
  setCategoryFilter: (c: string) => void;
  statusFilter: string;
  setStatusFilter: (s: string) => void;
  confidenceFilter: string;
  setConfidenceFilter: (c: string) => void;
}

export function ReviewFindingFilters({
  searchQuery, setSearchQuery,
  severityFilter, setSeverityFilter,
  categoryFilter, setCategoryFilter,
  statusFilter, setStatusFilter,
  confidenceFilter, setConfidenceFilter
}: ReviewFindingFiltersProps) {
  return (
    <div className="flex flex-col gap-4 p-4 bg-[#0F1726] border border-[#1E293B] rounded-lg mb-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
        <input
          type="text"
          placeholder="Search findings, components, or evidence..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:border-[#3B82F6]"
        />
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
          <option value="INFO">Info</option>
        </select>
        
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Categories</option>
          <option value="ARCHITECTURE">Architecture</option>
          <option value="DEPENDENCIES">Dependencies</option>
          <option value="BOUNDARIES">Boundaries</option>
          <option value="SECURITY">Security</option>
          <option value="SCALABILITY">Scalability</option>
          <option value="MAINTAINABILITY">Maintainability</option>
          <option value="PERFORMANCE">Performance</option>
        </select>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="ACKNOWLEDGED">Acknowledged</option>
          <option value="RESOLVED">Resolved</option>
          <option value="DISMISSED">Dismissed</option>
        </select>
        
        <select
          value={confidenceFilter}
          onChange={(e) => setConfidenceFilter(e.target.value)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Confidence</option>
          <option value="90">90%+</option>
          <option value="80">80%+</option>
          <option value="70">70%+</option>
        </select>
      </div>
    </div>
  );
}

import { Search, X } from "lucide-react";

interface GovernanceViolationFiltersProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  categoryFilter: string;
  onCategoryFilterChange: (c: string) => void;
  severityFilter: string;
  onSeverityFilterChange: (s: string) => void;
  statusFilter: string;
  onStatusFilterChange: (s: string) => void;
  policyFilter: string;
  onPolicyFilterChange: (p: string) => void;
  availablePolicies: { id: string; name: string }[];
}

export function GovernanceViolationFilters({
  searchQuery, onSearchChange,
  categoryFilter, onCategoryFilterChange,
  severityFilter, onSeverityFilterChange,
  statusFilter, onStatusFilterChange,
  policyFilter, onPolicyFilterChange,
  availablePolicies
}: GovernanceViolationFiltersProps) {

  const hasFilters = searchQuery !== "" || categoryFilter !== "All" || severityFilter !== "All" || statusFilter !== "All" || policyFilter !== "All Policies";

  return (
    <div className="flex flex-col sm:flex-row flex-wrap items-center gap-3 w-full mb-4">
      <div className="relative w-full sm:w-auto flex-1 min-w-[200px]">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search violations..."
          className="w-full pl-9 pr-4 py-1.5 bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:border-[#3B82F6]"
        />
      </div>

      <select
        value={categoryFilter}
        onChange={(e) => onCategoryFilterChange(e.target.value)}
        className="w-full sm:w-auto bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1.5 focus:outline-none focus:border-[#3B82F6]"
      >
        <option value="All">All Categories</option>
        <option value="Architecture">Architecture</option>
        <option value="Security">Security</option>
        <option value="Dependencies">Dependencies</option>
        <option value="Code Quality">Code Quality</option>
        <option value="Repository">Repository</option>
        <option value="Engineering">Engineering</option>
      </select>

      <select
        value={severityFilter}
        onChange={(e) => onSeverityFilterChange(e.target.value)}
        className="w-full sm:w-auto bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1.5 focus:outline-none focus:border-[#3B82F6]"
      >
        <option value="All">All Severities</option>
        <option value="Critical">Critical</option>
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
      </select>

      <select
        value={statusFilter}
        onChange={(e) => onStatusFilterChange(e.target.value)}
        className="w-full sm:w-auto bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1.5 focus:outline-none focus:border-[#3B82F6]"
      >
        <option value="All">All Status</option>
        <option value="Open">Open</option>
        <option value="Resolved">Resolved</option>
        <option value="Ignored">Ignored</option>
      </select>

      <select
        value={policyFilter}
        onChange={(e) => onPolicyFilterChange(e.target.value)}
        className="w-full sm:w-auto bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1.5 focus:outline-none focus:border-[#3B82F6]"
      >
        <option value="All Policies">All Policies</option>
        {availablePolicies.map(p => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>

      {hasFilters && (
        <button 
          onClick={() => {
            onSearchChange("");
            onCategoryFilterChange("All");
            onSeverityFilterChange("All");
            onStatusFilterChange("All");
            onPolicyFilterChange("All Policies");
          }}
          className="text-xs text-[#94A3B8] hover:text-[#F8FAFC] flex items-center gap-1 transition-colors shrink-0"
        >
          <X className="w-3 h-3" /> Clear
        </button>
      )}
    </div>
  );
}

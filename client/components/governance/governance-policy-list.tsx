import { GovernancePolicy, PolicyStatus } from "@/types/governance-ui";
import { Search, X } from "lucide-react";

interface GovernancePolicyListProps {
  policies: GovernancePolicy[];
  searchQuery: string;
  onSearchChange: (q: string) => void;
  statusFilter: string;
  onStatusFilterChange: (s: string) => void;
  categoryFilter: string;
  onCategoryFilterChange: (c: string) => void;
  onSelectPolicy: (policy: GovernancePolicy) => void;
}

export function GovernancePolicyList({
  policies,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  categoryFilter,
  onCategoryFilterChange,
  onSelectPolicy
}: GovernancePolicyListProps) {
  
  const getStatusColor = (status: PolicyStatus) => {
    switch (status) {
      case "Passing": return "text-[#22C55E] bg-[#22C55E]/10 border-[#22C55E]/20";
      case "At Risk": return "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20";
      case "Failing": return "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20";
      case "Disabled": return "text-[#94A3B8] bg-[#94A3B8]/10 border-[#94A3B8]/20";
    }
  };

  const getComplianceColor = (val: number) => {
    if (val >= 95) return "text-[#22C55E]";
    if (val >= 85) return "text-[#3B82F6]";
    if (val >= 75) return "text-[#F59E0B]";
    return "text-[#EF4444]";
  };

  const hasFilters = searchQuery !== "" || statusFilter !== "All" || categoryFilter !== "All";

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
        <h2 className="text-sm font-semibold text-[#F8FAFC]">Policy Compliance</h2>
        
        <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
          <div className="relative w-full sm:w-48">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search policies..."
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
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="w-full sm:w-auto bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-2 py-1.5 focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="All">All Status</option>
            <option value="Passing">Passing</option>
            <option value="At Risk">At Risk</option>
            <option value="Failing">Failing</option>
            <option value="Disabled">Disabled</option>
          </select>
          {hasFilters && (
            <button 
              onClick={() => { onSearchChange(""); onStatusFilterChange("All"); onCategoryFilterChange("All"); }}
              className="text-xs text-[#94A3B8] hover:text-[#F8FAFC] flex items-center gap-1 transition-colors shrink-0"
            >
              <X className="w-3 h-3" /> Clear
            </button>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead>
            <tr className="text-[#64748B] border-b border-[#1E293B]">
              <th className="pb-3 font-medium px-2">Policy</th>
              <th className="pb-3 font-medium px-2">Category</th>
              <th className="pb-3 font-medium px-2">Compliance</th>
              <th className="pb-3 font-medium px-2">Rules</th>
              <th className="pb-3 font-medium px-2">Violations</th>
              <th className="pb-3 font-medium px-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {policies.length > 0 ? (
              policies.map((policy) => (
                <tr 
                  key={policy.id} 
                  className="border-b border-[#1E293B]/50 hover:bg-[#141E2E] cursor-pointer transition-colors"
                  onClick={() => onSelectPolicy(policy)}
                  data-testid="policy-row"
                >
                  <td className="py-3 px-2">
                    <span className="font-medium text-[#F8FAFC]">{policy.name}</span>
                  </td>
                  <td className="py-3 px-2 text-[#94A3B8]">{policy.category}</td>
                  <td className="py-3 px-2">
                    <span className={`font-semibold ${getComplianceColor(policy.compliance)}`}>{policy.compliance}%</span>
                  </td>
                  <td className="py-3 px-2 text-[#CBD5E1]">{policy.ruleCount}</td>
                  <td className="py-3 px-2 text-[#CBD5E1]">{policy.violationCount}</td>
                  <td className="py-3 px-2">
                    <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${getStatusColor(policy.status)}`}>
                      {policy.status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="py-8 text-center text-[#64748B]">
                  No policies found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

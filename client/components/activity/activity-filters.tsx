import { ActivityFilterState, ActivityType, ActivitySeverity, ActivityStatus, ActorType } from "@/types/activity-ui";
import { Search, Filter, X } from "lucide-react";

interface Props {
  filters: ActivityFilterState;
  onChange: (updates: Partial<ActivityFilterState>) => void;
  onClear: () => void;
  resultCount: number;
}

export function ActivityFilters({ filters, onChange, onClear, resultCount }: Props) {
  const hasActiveFilters = 
    filters.search !== "" || 
    filters.type !== "ALL" || 
    filters.severity !== "ALL" || 
    filters.status !== "ALL" || 
    filters.actorType !== "ALL" || 
    filters.date !== "ALL";

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 mb-6">
      <div className="flex flex-col xl:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
          <input
            type="text"
            placeholder="Search events, components, projects..."
            value={filters.search}
            onChange={(e) => onChange({ search: e.target.value })}
            className="w-full pl-9 pr-10 py-2 bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:border-[#3B82F6]"
          />
          {filters.search && (
            <button 
              onClick={() => onChange({ search: "" })}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-[#F8FAFC]"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        
        {/* Dropdown Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <select 
            value={filters.type}
            onChange={(e) => onChange({ type: e.target.value as ActivityType | "ALL" })}
            className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] min-w-[130px]"
          >
            <option value="ALL">All Types</option>
            <option value="ANALYSIS">Analysis</option>
            <option value="ARCHITECTURE">Architecture</option>
            <option value="DEPENDENCY">Dependency</option>
            <option value="GOVERNANCE">Governance</option>
            <option value="AI_REVIEW">AI Review</option>
            <option value="DECISION">Decision</option>
            <option value="REPORT">Report</option>
            <option value="SETTINGS">Settings</option>
            <option value="PROJECT">Project</option>
            <option value="SYSTEM">System</option>
          </select>

          <select 
            value={filters.severity}
            onChange={(e) => onChange({ severity: e.target.value as ActivitySeverity | "ALL" })}
            className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="ALL">All Severities</option>
            <option value="INFO">Info</option>
            <option value="SUCCESS">Success</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>

          <select 
            value={filters.status}
            onChange={(e) => onChange({ status: e.target.value as ActivityStatus | "ALL" })}
            className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="ALL">All Statuses</option>
            <option value="COMPLETED">Completed</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="FAILED">Failed</option>
            <option value="RESOLVED">Resolved</option>
            <option value="UPDATED">Updated</option>
          </select>
          
          <select 
            value={filters.actorType}
            onChange={(e) => onChange({ actorType: e.target.value as ActorType | "ALL" })}
            className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="ALL">All Actors</option>
            <option value="USER">User</option>
            <option value="SYSTEM">System</option>
            <option value="AI">AI</option>
            <option value="AUTOMATION">Automation</option>
          </select>
          
          <select 
            value={filters.date}
            onChange={(e) => onChange({ date: e.target.value as "TODAY" | "YESTERDAY" | "LAST_7_DAYS" | "LAST_30_DAYS" | "ALL" })}
            className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
          >
            <option value="ALL">All Dates</option>
            <option value="TODAY">Today</option>
            <option value="YESTERDAY">Yesterday</option>
            <option value="LAST_7_DAYS">Last 7 Days</option>
            <option value="LAST_30_DAYS">Last 30 Days</option>
          </select>

          {(hasActiveFilters) && (
            <button 
              onClick={onClear}
              className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
            >
              <Filter className="h-3 w-3" />
              Clear
            </button>
          )}
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-[#1E293B] flex items-center justify-between text-xs text-[#64748B]">
        <span>Showing {resultCount} matching events</span>
      </div>
    </div>
  );
}



import { Search } from "lucide-react";
import { DecisionCategory, EffortLevel, ImpactLevel, RecommendationPriority, RecommendationStatus } from "@/types/decision-intelligence-ui";

interface RecommendationFiltersProps {
  searchQuery: string;
  setSearchQuery: (s: string) => void;
  categoryFilter: DecisionCategory | "ALL";
  setCategoryFilter: (c: DecisionCategory | "ALL") => void;
  priorityFilter: RecommendationPriority | "ALL";
  setPriorityFilter: (p: RecommendationPriority | "ALL") => void;
  statusFilter: RecommendationStatus | "ALL";
  setStatusFilter: (s: RecommendationStatus | "ALL") => void;
  impactFilter: ImpactLevel | "ALL";
  setImpactFilter: (i: ImpactLevel | "ALL") => void;
  effortFilter: EffortLevel | "ALL";
  setEffortFilter: (e: EffortLevel | "ALL") => void;
}

export function RecommendationFilters({
  searchQuery, setSearchQuery,
  categoryFilter, setCategoryFilter,
  priorityFilter, setPriorityFilter,
  statusFilter, setStatusFilter,
  impactFilter, setImpactFilter,
  effortFilter, setEffortFilter
}: RecommendationFiltersProps) {
  return (
    <div className="flex flex-col gap-4 p-4 bg-[#0F1726] border border-[#1E293B] rounded-lg mb-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
        <input
          type="text"
          placeholder="Search recommendations, evidence, components..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:border-[#3B82F6]"
        />
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value as never)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Categories</option>
          <option value="ARCHITECTURE">Architecture</option>
          <option value="DEPENDENCIES">Dependencies</option>
          <option value="SECURITY">Security</option>
          <option value="CODE_QUALITY">Code Quality</option>
          <option value="PERFORMANCE">Performance</option>
          <option value="MAINTAINABILITY">Maintainability</option>
        </select>
        
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value as never)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Priorities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as never)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Statuses</option>
          <option value="NEW">New</option>
          <option value="REVIEWED">Reviewed</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="COMPLETED">Completed</option>
          <option value="DISMISSED">Dismissed</option>
        </select>
        
        <select
          value={impactFilter}
          onChange={(e) => setImpactFilter(e.target.value as never)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Impacts</option>
          <option value="HIGH">High Impact</option>
          <option value="MEDIUM">Medium Impact</option>
          <option value="LOW">Low Impact</option>
        </select>
        
        <select
          value={effortFilter}
          onChange={(e) => setEffortFilter(e.target.value as never)}
          className="bg-[#080D18] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1] focus:outline-none focus:border-[#3B82F6]"
        >
          <option value="ALL">All Efforts</option>
          <option value="HIGH">High Effort</option>
          <option value="MEDIUM">Medium Effort</option>
          <option value="LOW">Low Effort</option>
        </select>
      </div>
    </div>
  );
}

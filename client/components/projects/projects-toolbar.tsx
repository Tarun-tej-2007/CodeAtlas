import { Search, Filter, ArrowUpDown } from "lucide-react";
import { useEffect, useState } from "react";

interface ProjectsToolbarProps {
  search: string;
  onSearchChange: (search: string) => void;
  visibility: string;
  onVisibilityChange: (visibility: string) => void;
  sortBy: string;
  onSortByChange: (sortBy: string) => void;
  order: "asc" | "desc";
  onOrderChange: (order: "asc" | "desc") => void;
}

export function ProjectsToolbar({
  search,
  onSearchChange,
  visibility,
  onVisibilityChange,
  sortBy,
  onSortByChange,
  order,
  onOrderChange,
}: ProjectsToolbarProps) {
  const [localSearch, setLocalSearch] = useState(search);

  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchChange(localSearch);
    }, 300);
    return () => clearTimeout(timer);
  }, [localSearch, onSearchChange]);

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between py-4">
      <div className="relative w-full sm:max-w-xs">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <Search className="h-4 w-4 text-[#64748B]" />
        </div>
        <input
          type="text"
          placeholder="Search projects..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="block w-full rounded-md border border-[#1E293B] bg-[#0F1726] py-1.5 pl-9 pr-3 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#3B82F6] focus:outline-hidden focus:ring-1 focus:ring-[#3B82F6]"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex items-center">
          <Filter className="absolute left-2.5 h-3.5 w-3.5 text-[#64748B]" />
          <select
            value={visibility}
            onChange={(e) => onVisibilityChange(e.target.value)}
            className="rounded-md border border-[#1E293B] bg-[#0F1726] py-1.5 pl-8 pr-8 text-xs text-[#CBD5E1] focus:border-[#3B82F6] focus:outline-hidden appearance-none"
          >
            <option value="">Visibility: All</option>
            <option value="public">Public</option>
            <option value="private">Private</option>
            <option value="internal">Internal</option>
          </select>
        </div>

        <select
          value={sortBy}
          onChange={(e) => onSortByChange(e.target.value)}
          className="rounded-md border border-[#1E293B] bg-[#0F1726] py-1.5 pl-3 pr-8 text-xs text-[#CBD5E1] focus:border-[#3B82F6] focus:outline-hidden appearance-none"
        >
          <option value="name">Sort: Name</option>
          <option value="created_at">Sort: Created</option>
          <option value="updated_at">Sort: Updated</option>
        </select>

        <button
          type="button"
          onClick={() => onOrderChange(order === "asc" ? "desc" : "asc")}
          className="flex h-[30px] items-center justify-center rounded-md border border-[#1E293B] bg-[#0F1726] px-2 text-[#CBD5E1] hover:bg-[#141E2E] transition-colors"
          title={order === "asc" ? "Ascending" : "Descending"}
        >
          <ArrowUpDown className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

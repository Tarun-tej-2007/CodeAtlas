import { Search, X } from "lucide-react";

interface SettingsSearchProps {
  query: string;
  onChange: (query: string) => void;
}

export function SettingsSearch({ query, onChange }: SettingsSearchProps) {
  return (
    <div className="relative mb-6">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B]" />
      <input
        type="text"
        placeholder="Search settings..."
        value={query}
        onChange={(e) => onChange(e.target.value)}
        className="w-full pl-9 pr-10 py-2 bg-[#0F1726] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] focus:outline-none focus:border-[#3B82F6]"
      />
      {query && (
        <button 
          onClick={() => onChange("")}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-[#F8FAFC]"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}

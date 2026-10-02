import { CategoryCompliance, PolicyCategory } from "@/types/governance-ui";

interface GovernanceCategoryComplianceProps {
  categories: CategoryCompliance[];
  onCategoryClick: (category: PolicyCategory) => void;
}

export function GovernanceCategoryCompliance({ categories, onCategoryClick }: GovernanceCategoryComplianceProps) {
  const getColor = (comp: number) => {
    if (comp >= 95) return "bg-[#22C55E]"; // Green
    if (comp >= 85) return "bg-[#3B82F6]"; // Blue
    if (comp >= 75) return "bg-[#F59E0B]"; // Warning
    return "bg-[#EF4444]"; // Danger
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 h-full flex flex-col">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4">Category Compliance</h2>
      <div className="flex-1 flex flex-col gap-4">
        {categories.map((c) => (
          <div 
            key={c.category}
            className="group cursor-pointer"
            onClick={() => onCategoryClick(c.category)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter') onCategoryClick(c.category); }}
          >
            <div className="flex justify-between text-xs mb-1">
              <span className="text-[#94A3B8] group-hover:text-[#F8FAFC] transition-colors">{c.category}</span>
              <span className="text-[#F8FAFC] font-medium">{c.compliance}%</span>
            </div>
            <div className="h-2 bg-[#080D18] rounded-full overflow-hidden border border-[#1E293B]">
              <div 
                className={`h-full ${getColor(c.compliance)} transition-all duration-500`} 
                style={{ width: `${c.compliance}%` }} 
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

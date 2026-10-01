import { DecisionCategoryStats } from "@/types/decision-intelligence-ui";

interface DecisionCategoryBreakdownProps {
  stats: DecisionCategoryStats[];
}

export function DecisionCategoryBreakdown({ stats }: DecisionCategoryBreakdownProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <h3 className="text-sm font-bold text-[#F8FAFC] mb-4 uppercase tracking-wider">Category Breakdown</h3>
      <div className="space-y-4">
        {stats.map((stat) => (
          <div key={stat.category}>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-medium text-[#CBD5E1]">{stat.category.replace("_", " ")}</span>
              <span className="text-[#94A3B8]">
                {stat.recommendations} recs ({stat.highPriority} High)
              </span>
            </div>
            <div className="w-full bg-[#1E293B] rounded-full h-1.5 overflow-hidden flex">
              {/* High Priority segment */}
              <div 
                className="bg-[#EF4444] h-1.5" 
                style={{ width: `${stat.recommendations > 0 ? (stat.highPriority / stat.recommendations) * 100 : 0}%` }}
              />
              {/* Other recs segment */}
              <div 
                className="bg-[#3B82F6] h-1.5" 
                style={{ width: `${stat.recommendations > 0 ? ((stat.recommendations - stat.highPriority) / stat.recommendations) * 100 : 0}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

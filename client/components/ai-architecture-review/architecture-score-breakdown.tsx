import { ArchitectureReviewCategory } from "@/types/ai-architecture-review-ui";

interface ArchitectureScoreBreakdownProps {
  categories: ArchitectureReviewCategory[];
}

export function ArchitectureScoreBreakdown({ categories }: ArchitectureScoreBreakdownProps) {
  const getColor = (score: number) => {
    if (score >= 90) return "bg-[#10B981]";
    if (score >= 80) return "bg-[#3B82F6]";
    if (score >= 70) return "bg-[#F59E0B]";
    return "bg-[#EF4444]";
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <h3 className="text-sm font-bold text-[#F8FAFC] mb-5 uppercase tracking-wider">Score Breakdown</h3>
      <div className="space-y-5">
        {categories.map((c) => (
          <div key={c.category}>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold text-[#CBD5E1] tracking-wide">{c.category.charAt(0) + c.category.slice(1).toLowerCase()}</span>
              <span className="font-bold text-[#F8FAFC]">{c.score}%</span>
            </div>
            <div className="w-full bg-[#1E293B] rounded-full h-1.5 overflow-hidden mb-1.5">
              <div 
                className={`${getColor(c.score)} h-1.5 rounded-full`} 
                style={{ width: `${c.score}%` }}
              />
            </div>
            <p className="text-[11px] text-[#64748B] italic">&quot;{c.explanation}&quot;</p>
          </div>
        ))}
      </div>
    </div>
  );
}

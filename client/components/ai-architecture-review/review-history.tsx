import { ArchitectureReviewHistory } from "@/types/ai-architecture-review-ui";
import { History, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface ReviewHistoryProps {
  history: ArchitectureReviewHistory[];
}

export function ReviewHistory({ history }: ReviewHistoryProps) {
  const getChangeIcon = (change: string) => {
    switch (change) {
      case "UP": return <TrendingUp className="h-4 w-4 text-[#10B981]" />;
      case "DOWN": return <TrendingDown className="h-4 w-4 text-[#EF4444]" />;
      default: return <Minus className="h-4 w-4 text-[#64748B]" />;
    }
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <div className="flex items-center gap-2 mb-4">
        <History className="h-5 w-5 text-[#94A3B8]" />
        <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Review History</h3>
      </div>
      
      <div className="relative pl-3 border-l border-[#1E293B] space-y-4 ml-2">
        {history.map((h, i) => (
          <div key={h.id} className="relative">
            <div className={`absolute -left-[17px] top-1 h-2 w-2 rounded-full ${i === 0 ? "bg-[#3B82F6]" : "bg-[#64748B]"}`} />
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs font-semibold text-[#CBD5E1] mb-0.5">{h.date}</div>
                <div className="text-[10px] text-[#64748B]">
                  {h.findings} findings • {h.recommendations} recommendations
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-[#F8FAFC]">{h.score}</span>
                {getChangeIcon(h.change)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

import { TechnicalDebtSummary } from "@/types/decision-intelligence-ui";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";

interface TechnicalDebtAnalysisProps {
  debt: TechnicalDebtSummary;
}

export function TechnicalDebtAnalysis({ debt }: TechnicalDebtAnalysisProps) {
  const getTrendIcon = () => {
    if (debt.trend === "UP") return <TrendingUp className="h-4 w-4 text-[#EF4444]" />;
    if (debt.trend === "DOWN") return <TrendingDown className="h-4 w-4 text-[#10B981]" />;
    return <Minus className="h-4 w-4 text-[#94A3B8]" />;
  };

  const getTrendColor = () => {
    if (debt.trend === "UP") return "text-[#EF4444]";
    if (debt.trend === "DOWN") return "text-[#10B981]";
    return "text-[#94A3B8]";
  };

  const diff = debt.total - debt.previousTotal;
  const sign = diff > 0 ? "+" : "";

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-5">
      <h3 className="text-sm font-bold text-[#F8FAFC] mb-4 uppercase tracking-wider">Technical Debt</h3>
      
      <div className="flex items-end gap-3 mb-6">
        <div className="text-3xl font-bold text-[#F8FAFC]">{debt.total}</div>
        <div className="text-sm text-[#94A3B8] mb-1">items</div>
        <div className={`flex items-center gap-1 ml-auto text-sm font-medium ${getTrendColor()}`}>
          {getTrendIcon()}
          <span>{sign}{diff} from last month</span>
        </div>
      </div>

      <div className="space-y-3">
        {debt.items.map(item => (
          <div key={item.id} className="flex items-center justify-between">
            <span className="text-sm text-[#CBD5E1]">{item.category}</span>
            <div className="flex items-center gap-3 w-1/2">
              <div className="flex-1 bg-[#1E293B] h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-[#8B5CF6] h-full rounded-full"
                  style={{ width: `${(item.count / debt.total) * 100}%` }}
                />
              </div>
              <span className="text-xs text-[#94A3B8] w-4 text-right">{item.count}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

import { EvolutionSnapshot } from "@/types/architecture-evolution-ui";
import { ArrowRight } from "lucide-react";

interface EvolutionRiskTrendProps {
  baselineSnapshot: EvolutionSnapshot;
  currentSnapshot: EvolutionSnapshot;
}

export function EvolutionRiskTrend({ baselineSnapshot, currentSnapshot }: EvolutionRiskTrendProps) {
  const renderRiskRow = (label: string, from: number, to: number, colorClass: string) => {
    const isImproved = to < from;
    const isWorse = to > from;
    
    return (
      <div className="flex items-center justify-between py-2 border-b border-[#1E293B]/50 last:border-0">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${colorClass}`} />
          <span className="text-sm font-medium text-[#F8FAFC]">{label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-[#94A3B8]">{from}</span>
          <ArrowRight className="w-3 h-3 text-[#64748B]" />
          <span className={`text-sm font-semibold ${isImproved ? 'text-[#22C55E]' : isWorse ? 'text-[#EF4444]' : 'text-[#F8FAFC]'}`}>{to}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4">Risk Trend</h2>
      
      <div className="flex-1 flex flex-col justify-center gap-2">
        {renderRiskRow("Critical", baselineSnapshot.riskCounts.Critical, currentSnapshot.riskCounts.Critical, "bg-[#EF4444]")}
        {renderRiskRow("High", baselineSnapshot.riskCounts.High, currentSnapshot.riskCounts.High, "bg-[#F59E0B]")}
        {renderRiskRow("Medium", baselineSnapshot.riskCounts.Medium, currentSnapshot.riskCounts.Medium, "bg-[#3B82F6]")}
        {renderRiskRow("Low", baselineSnapshot.riskCounts.Low, currentSnapshot.riskCounts.Low, "bg-[#94A3B8]")}
      </div>
    </div>
  );
}

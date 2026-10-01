import { DecisionHealth } from "@/types/decision-intelligence-ui";
import { Sparkles } from "lucide-react";

interface DecisionSummaryProps {
  health: DecisionHealth;
  topCategory: string;
}

export function DecisionSummary({ health, topCategory }: DecisionSummaryProps) {
  return (
    <div className="bg-gradient-to-br from-[#0F1726] to-[#0B1220] border border-[#3B82F6]/20 rounded-lg p-5 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <Sparkles className="h-16 w-16 text-[#3B82F6]" />
      </div>
      
      <div className="flex items-center gap-2 mb-3 relative z-10">
        <Sparkles className="h-4 w-4 text-[#3B82F6]" />
        <h3 className="text-sm font-bold text-[#F8FAFC] uppercase tracking-wider">Intelligence Summary</h3>
      </div>
      
      <div className="space-y-3 relative z-10">
        <p className="text-sm text-[#CBD5E1] leading-relaxed">
          Based on the latest analysis, <strong className="text-[#F8FAFC]">{health.highPriority} high-priority recommendations</strong> require engineering attention to address immediate structural risks.
        </p>
        <p className="text-sm text-[#CBD5E1] leading-relaxed">
          <strong className="text-[#F8FAFC]">{topCategory}</strong> represents the largest concentration of decision risk, contributing significantly to the {health.technicalDebt} identified technical debt items.
        </p>
        <p className="text-sm text-[#CBD5E1] leading-relaxed">
          Resolving the strategic Quick Wins could yield up to <strong className="text-[#F8FAFC]">{health.potentialSavings}% potential savings</strong> in maintenance effort over the next two quarters.
        </p>
      </div>
    </div>
  );
}

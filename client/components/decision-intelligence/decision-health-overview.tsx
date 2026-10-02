import { DecisionHealth } from "@/types/decision-intelligence-ui";
import { Activity, AlertTriangle, CheckSquare, Coins, ListChecks, ShieldAlert } from "lucide-react";

interface DecisionHealthOverviewProps {
  health: DecisionHealth;
}

export function DecisionHealthOverview({ health }: DecisionHealthOverviewProps) {
  const metrics = [
    { label: "Decision Health", value: `${health.score} / 100`, icon: Activity, color: "text-[#10B981]", bg: "bg-[#10B981]/10", border: "border-[#10B981]/20" },
    { label: "Recommendations", value: health.recommendations, icon: ListChecks, color: "text-[#3B82F6]", bg: "bg-[#3B82F6]/10", border: "border-[#3B82F6]/20" },
    { label: "High Priority", value: health.highPriority, icon: AlertTriangle, color: "text-[#F59E0B]", bg: "bg-[#F59E0B]/10", border: "border-[#F59E0B]/20" },
    { label: "Architecture Risks", value: health.architectureRisks, icon: ShieldAlert, color: "text-[#EF4444]", bg: "bg-[#EF4444]/10", border: "border-[#EF4444]/20" },
    { label: "Technical Debt", value: health.technicalDebt, icon: CheckSquare, color: "text-[#8B5CF6]", bg: "bg-[#8B5CF6]/10", border: "border-[#8B5CF6]/20" },
    { label: "Potential Savings", value: `${health.potentialSavings}%`, icon: Coins, color: "text-[#14B8A6]", bg: "bg-[#14B8A6]/10", border: "border-[#14B8A6]/20" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {metrics.map((m, i) => (
        <div key={i} className="flex flex-col p-4 rounded-lg bg-[#0F1726] border border-[#1E293B]">
          <div className="flex items-center gap-3 mb-2">
            <div className={`flex h-8 w-8 items-center justify-center rounded-md border ${m.bg} ${m.color} ${m.border}`}>
              <m.icon className="h-4 w-4" />
            </div>
            <div className="text-xs font-semibold uppercase tracking-wider text-[#64748B]">{m.label}</div>
          </div>
          <div className="mt-1 text-2xl font-bold text-[#F8FAFC]">{m.value}</div>
        </div>
      ))}
    </div>
  );
}

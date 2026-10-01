import { GovernanceStats } from "@/types/governance-ui";
import { Info } from "lucide-react";

interface GovernanceSummaryProps {
  stats: GovernanceStats;
}

export function GovernanceSummary({ stats }: GovernanceSummaryProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex gap-4 mt-6">
      <div className="shrink-0 pt-1">
        <Info className="w-5 h-5 text-[#3B82F6]" />
      </div>
      <div>
        <h2 className="text-sm font-semibold text-[#F8FAFC] mb-2">Governance Summary</h2>
        <div className="text-sm text-[#94A3B8] leading-relaxed space-y-1">
          <p><strong className="text-[#F8FAFC]">{stats.health.compliance}%</strong> of active policies are currently compliant.</p>
          <p><strong className="text-[#EF4444]">{stats.health.criticalViolations}</strong> critical violations require attention.</p>
          <p><strong className="text-[#F8FAFC]">{stats.health.activeExceptions}</strong> active exceptions are currently approved.</p>
          <p>Compliance has improved by <strong className="text-[#22C55E]">4.1%</strong> since the previous evaluation.</p>
        </div>
      </div>
    </div>
  );
}

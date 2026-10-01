import { GovernanceHealth } from "@/types/governance-ui";
import { ShieldCheck, CheckCircle2, FileText, AlertTriangle, XCircle, Unlock } from "lucide-react";

interface GovernanceHealthOverviewProps {
  health: GovernanceHealth;
}

export function GovernanceHealthOverview({ health }: GovernanceHealthOverviewProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <ShieldCheck className="w-4 h-4 text-[#3B82F6]" />
          <span className="text-xs uppercase font-semibold">Governance Health</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {health.score} <span className="text-sm text-[#64748B] font-medium">/ 100</span>
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />
          <span className="text-xs uppercase font-semibold">Compliance</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {health.compliance}%
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <FileText className="w-4 h-4" />
          <span className="text-xs uppercase font-semibold">Policies</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {health.policyCount}
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
          <span className="text-xs uppercase font-semibold">Open Violations</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {health.openViolations}
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <XCircle className="w-4 h-4 text-[#EF4444]" />
          <span className="text-xs uppercase font-semibold">Critical</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {health.criticalViolations}
        </div>
      </div>

      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col">
        <div className="flex items-center gap-2 text-[#94A3B8] mb-2">
          <Unlock className="w-4 h-4 text-[#8B5CF6]" />
          <span className="text-xs uppercase font-semibold">Exceptions</span>
        </div>
        <div className="text-2xl font-semibold text-[#F8FAFC]">
          {health.activeExceptions}
        </div>
      </div>
    </div>
  );
}

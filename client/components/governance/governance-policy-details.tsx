import { GovernancePolicy } from "@/types/governance-ui";
import { X, ShieldCheck, Tag, User, Layers, Info } from "lucide-react";
import Link from "next/link";

interface GovernancePolicyDetailsProps {
  policy: GovernancePolicy;
  onClose: () => void;
}

export function GovernancePolicyDetails({ policy, onClose }: GovernancePolicyDetailsProps) {
  const getComplianceColor = (val: number) => {
    if (val >= 95) return "text-[#22C55E]";
    if (val >= 85) return "text-[#3B82F6]";
    if (val >= 75) return "text-[#F59E0B]";
    return "text-[#EF4444]";
  };

  return (
    <div className="flex flex-col h-full bg-[#0F1726] border-l border-[#1E293B] w-80 md:w-96 shrink-0">
      <div className="flex items-center justify-between p-4 border-b border-[#1E293B]">
        <h2 className="text-sm font-semibold text-[#F8FAFC]">Policy Details</h2>
        <button 
          onClick={onClose}
          className="p-1 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 flex flex-col gap-6">
        <div>
          <h3 className="text-lg font-semibold text-[#F8FAFC] mb-1">{policy.name}</h3>
          <p className="text-sm text-[#94A3B8] leading-relaxed">{policy.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Category</span>
            <div className="flex items-center gap-2 text-sm text-[#F8FAFC]">
              <Tag className="w-4 h-4 text-[#8B5CF6]" />
              {policy.category}
            </div>
          </div>
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Owner</span>
            <div className="flex items-center gap-2 text-sm text-[#F8FAFC]">
              <User className="w-4 h-4 text-[#3B82F6]" />
              {policy.owner}
            </div>
          </div>
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Compliance</span>
            <div className={`flex items-center gap-2 text-lg font-semibold ${getComplianceColor(policy.compliance)}`}>
              {policy.compliance}%
            </div>
          </div>
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Status</span>
            <div className="flex items-center gap-2 text-sm text-[#F8FAFC]">
              {policy.status}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#080D18] p-3 rounded-md border border-[#1E293B]">
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Rules</span>
            <span className="text-xl font-semibold text-[#F8FAFC]">{policy.ruleCount}</span>
          </div>
          <div className="bg-[#080D18] p-3 rounded-md border border-[#1E293B]">
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Violations</span>
            <span className={`text-xl font-semibold ${policy.violationCount > 0 ? "text-[#EF4444]" : "text-[#22C55E]"}`}>{policy.violationCount}</span>
          </div>
        </div>

        <div className="mt-auto pt-4 flex flex-col gap-2">
          <button className="flex items-center justify-center gap-2 w-full py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors">
            <Info className="w-4 h-4" /> View Violations
          </button>
          <Link href="/architecture" className="flex items-center justify-center gap-2 w-full py-2 bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors">
            <Layers className="w-4 h-4" /> View Architecture
          </Link>
        </div>
      </div>
    </div>
  );
}

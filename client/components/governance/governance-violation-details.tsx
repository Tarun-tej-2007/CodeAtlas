import { GovernanceViolation, GovernancePolicy } from "@/types/governance-ui";
import { X, AlertTriangle, Layers, GitMerge, FileText, CheckCircle2, ShieldAlert } from "lucide-react";
import Link from "next/link";

interface GovernanceViolationDetailsProps {
  violation: GovernanceViolation;
  policy?: GovernancePolicy;
  onClose: () => void;
  onMarkResolved: (id: string) => void;
  onRequestException: (id: string) => void;
}

export function GovernanceViolationDetails({ violation, policy, onClose, onMarkResolved, onRequestException }: GovernanceViolationDetailsProps) {
  const isResolved = violation.status === "Resolved";

  return (
    <div className="flex flex-col h-full bg-[#0F1726] border-l border-[#1E293B] w-80 md:w-96 shrink-0 z-50">
      <div className="flex items-center justify-between p-4 border-b border-[#1E293B]">
        <h2 className="text-sm font-semibold text-[#F8FAFC]">Violation Details</h2>
        <button 
          onClick={onClose}
          className="p-1 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 flex flex-col gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${
              violation.severity === "Critical" ? "text-[#EF4444] border-[#EF4444]/20 bg-[#EF4444]/10" :
              violation.severity === "High" ? "text-[#F59E0B] border-[#F59E0B]/20 bg-[#F59E0B]/10" :
              violation.severity === "Medium" ? "text-[#3B82F6] border-[#3B82F6]/20 bg-[#3B82F6]/10" :
              "text-[#94A3B8] border-[#94A3B8]/20 bg-[#94A3B8]/10"
            }`}>
              {violation.severity}
            </span>
            <span className={`text-xs font-semibold uppercase ${isResolved ? "text-[#22C55E]" : "text-[#F59E0B]"}`}>
              {violation.status}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-[#F8FAFC] mb-1">{violation.message}</h3>
          <p className="text-sm text-[#94A3B8] leading-relaxed">{violation.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Component</span>
            <div className="text-sm text-[#F8FAFC] break-all">{violation.component}</div>
          </div>
          <div>
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Detected</span>
            <div className="text-sm text-[#F8FAFC]">{violation.date}</div>
          </div>
          <div className="col-span-2">
            <span className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Policy</span>
            <div className="text-sm text-[#F8FAFC]">{policy?.name || violation.policyId}</div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-[#1E293B] flex flex-col gap-2">
          {!isResolved && (
            <>
              <button 
                onClick={() => onMarkResolved(violation.id)}
                className="flex items-center justify-center gap-2 w-full py-2 bg-[#10B981] hover:bg-[#059669] text-white text-sm font-medium rounded-lg transition-colors"
              >
                <CheckCircle2 className="w-4 h-4" /> Mark Resolved
              </button>
              <button 
                onClick={() => onRequestException(violation.id)}
                className="flex items-center justify-center gap-2 w-full py-2 bg-[#0F1726] hover:bg-[#1E293B] border border-[#1E293B] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors"
              >
                <ShieldAlert className="w-4 h-4" /> Request Exception
              </button>
            </>
          )}
          <Link href="/architecture" className="flex items-center justify-center gap-2 w-full py-2 bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors mt-2">
            <Layers className="w-4 h-4" /> View Architecture
          </Link>
          <Link href="/graph" className="flex items-center justify-center gap-2 w-full py-2 bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] text-sm font-medium rounded-lg transition-colors">
            <GitMerge className="w-4 h-4" /> View Dependency Graph
          </Link>
        </div>
      </div>
    </div>
  );
}

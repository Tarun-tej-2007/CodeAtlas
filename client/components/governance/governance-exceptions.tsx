import { GovernanceException } from "@/types/governance-ui";
import { Clock, User } from "lucide-react";

interface GovernanceExceptionsProps {
  exceptions: GovernanceException[];
}

export function GovernanceExceptions({ exceptions }: GovernanceExceptionsProps) {
  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg p-4 flex flex-col h-full">
      <h2 className="text-sm font-semibold text-[#F8FAFC] mb-4">Active Exceptions</h2>
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 flex flex-col gap-4">
        {exceptions.map(exc => (
          <div key={exc.id} className="bg-[#080D18] border border-[#1E293B] rounded-md p-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-[#F8FAFC] truncate" title={exc.component}>{exc.component}</h3>
              <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border shrink-0 ${
                exc.status === "Expiring Soon" ? "text-[#F59E0B] border-[#F59E0B]/20 bg-[#F59E0B]/10" :
                "text-[#3B82F6] border-[#3B82F6]/20 bg-[#3B82F6]/10"
              }`}>
                {exc.status}
              </span>
            </div>
            <p className="text-xs text-[#94A3B8] mb-3 line-clamp-2">{exc.reason}</p>
            <div className="flex items-center justify-between text-xs text-[#64748B]">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" /> Expires: {exc.expiry}
              </div>
              <div className="flex items-center gap-1">
                <User className="w-3 h-3" /> {exc.approvedBy}
              </div>
            </div>
          </div>
        ))}
        {exceptions.length === 0 && (
          <div className="text-sm text-[#64748B] text-center py-4">No active exceptions.</div>
        )}
      </div>
    </div>
  );
}

import { X } from "lucide-react";
import { useState } from "react";

interface GovernanceRequestExceptionProps {
  violationId: string;
  policyId: string;
  onClose: () => void;
  onSubmit: (violationId: string, reason: string, expiry: string) => void;
}

export function GovernanceRequestException({ violationId, policyId, onClose, onSubmit }: GovernanceRequestExceptionProps) {
  const [reason, setReason] = useState("");
  const [expiry, setExpiry] = useState("2026-11-01");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(violationId, reason, expiry);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#080D18]/80 backdrop-blur-sm p-4">
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg w-full max-w-lg shadow-2xl flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-[#1E293B]">
          <h2 className="text-sm font-semibold text-[#F8FAFC]">Request Governance Exception</h2>
          <button 
            onClick={onClose}
            className="p-1 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 flex flex-col gap-4">
          <div>
            <label className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Policy</label>
            <input 
              type="text" 
              disabled 
              value={policyId}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#94A3B8] px-3 py-2 cursor-not-allowed"
            />
          </div>
          <div>
            <label className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Violation ID</label>
            <input 
              type="text" 
              disabled 
              value={violationId}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#94A3B8] px-3 py-2 cursor-not-allowed"
            />
          </div>
          <div>
            <label className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Reason for Exception</label>
            <textarea 
              required
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Explain why this exception is needed..."
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] placeholder:text-[#64748B] px-3 py-2 focus:outline-none focus:border-[#3B82F6] h-24 resize-none"
            />
          </div>
          <div>
            <label className="text-xs text-[#64748B] uppercase font-semibold mb-1 block">Expiration Date</label>
            <input 
              type="date"
              required
              value={expiry}
              onChange={(e) => setExpiry(e.target.value)}
              className="w-full bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-3 py-2 focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
          <div className="pt-2 flex justify-end gap-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-[#94A3B8] hover:text-[#F8FAFC] font-medium transition-colors">
              Cancel
            </button>
            <button type="submit" className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-sm font-medium rounded-md transition-colors">
              Submit Request
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

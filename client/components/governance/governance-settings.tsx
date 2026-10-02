import { X } from "lucide-react";

interface GovernanceSettingsProps {
  onClose: () => void;
}

export function GovernanceSettings({ onClose }: GovernanceSettingsProps) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#080D18]/80 backdrop-blur-sm p-4">
      <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg w-full max-w-lg shadow-2xl flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-[#1E293B]">
          <h2 className="text-sm font-semibold text-[#F8FAFC]">Governance Settings</h2>
          <button 
            onClick={onClose}
            className="p-1 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 flex flex-col gap-6">
          <div>
            <h3 className="text-xs text-[#64748B] uppercase font-semibold mb-3">Enabled Policies</h3>
            <div className="flex flex-col gap-2">
              {["Architecture Layering", "Dependency Direction", "Domain Isolation", "Security Baseline", "Code Complexity", "Testing Coverage"].map((policy) => (
                <div key={policy} className="flex items-center justify-between">
                  <span className="text-sm text-[#CBD5E1]">{policy}</span>
                  <div className="w-10 h-5 bg-[#3B82F6] rounded-full relative cursor-pointer">
                    <div className="absolute right-1 top-1 w-3 h-3 bg-white rounded-full" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xs text-[#64748B] uppercase font-semibold mb-3">Enforcement Level</h3>
            <select className="w-full bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-3 py-2 focus:outline-none focus:border-[#3B82F6]">
              <option>Warning Only</option>
              <option>Blocking (Fail Build)</option>
            </select>
          </div>

          <div>
            <h3 className="text-xs text-[#64748B] uppercase font-semibold mb-3">Evaluation Frequency</h3>
            <select className="w-full bg-[#080D18] border border-[#1E293B] rounded-md text-sm text-[#F8FAFC] px-3 py-2 focus:outline-none focus:border-[#3B82F6]">
              <option>On every commit</option>
              <option>Daily</option>
              <option>Weekly</option>
            </select>
          </div>
        </div>

        <div className="p-4 border-t border-[#1E293B] flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 text-sm text-[#94A3B8] hover:text-[#F8FAFC] font-medium transition-colors">
            Cancel
          </button>
          <button onClick={onClose} className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-sm font-medium rounded-md transition-colors">
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}

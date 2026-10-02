import { X, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { ReportFormat, ReportType } from "@/types/reports-ui";

interface ReportSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ReportSettings({ isOpen, onClose }: ReportSettingsProps) {
  const [defaultFormat, setDefaultFormat] = useState<ReportFormat>("PDF");
  const [defaultType, setDefaultType] = useState<ReportType>("COMPREHENSIVE");
  const [retention, setRetention] = useState("Last 30 Reports");
  const [includes, setIncludes] = useState({
    findings: true,
    recommendations: true,
    architectureDiagram: true,
    governance: true,
    technicalDebt: true,
  });

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 z-50 bg-[#080D18]/80 backdrop-blur-sm flex items-center justify-center p-4"
        onClick={onClose}
      />
      
      <div className="fixed inset-0 sm:inset-auto sm:top-1/2 sm:left-1/2 sm:-translate-x-1/2 sm:-translate-y-1/2 z-50 w-full sm:w-[500px] sm:max-h-[85vh] bg-[#0B1220] border border-[#1E293B] shadow-2xl sm:rounded-xl flex flex-col overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-[#1E293B]">
          <div>
            <h2 className="text-lg font-bold text-[#F8FAFC]">Report Settings</h2>
            <p className="text-xs text-[#94A3B8] mt-1">Configure default preferences for generating reports.</p>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Default Format</label>
              <select
                value={defaultFormat}
                onChange={(e) => setDefaultFormat(e.target.value as ReportFormat)}
                className="w-full bg-[#0F1726] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              >
                <option value="PDF">PDF Document</option>
                <option value="HTML">Interactive HTML</option>
                <option value="JSON">Raw JSON Data</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Default Report Type</label>
              <select
                value={defaultType}
                onChange={(e) => setDefaultType(e.target.value as ReportType)}
                className="w-full bg-[#0F1726] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              >
                <option value="COMPREHENSIVE">Comprehensive</option>
                <option value="REPOSITORY_ANALYSIS">Repository Analysis</option>
                <option value="ARCHITECTURE">Architecture</option>
                <option value="DEPENDENCY">Dependency</option>
                <option value="GOVERNANCE">Governance</option>
                <option value="EVOLUTION">Evolution</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Report Retention</label>
              <select
                value={retention}
                onChange={(e) => setRetention(e.target.value)}
                className="w-full bg-[#0F1726] border border-[#1E293B] rounded-md px-3 py-2 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              >
                <option value="Last 10 Reports">Last 10 Reports</option>
                <option value="Last 30 Reports">Last 30 Reports</option>
                <option value="All Reports">All Reports</option>
              </select>
            </div>
          </div>
          
          <div className="space-y-3 pt-2 border-t border-[#1E293B]">
            <label className="text-xs font-semibold uppercase tracking-wider text-[#F8FAFC]">Always Include</label>
            <div className="space-y-2">
              {Object.entries(includes).map(([key, value]) => (
                <label key={key} className="flex items-center gap-3 cursor-pointer group">
                  <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${
                    value 
                      ? 'bg-[#3B82F6] border-[#3B82F6]' 
                      : 'bg-[#0F1726] border-[#334155] group-hover:border-[#64748B]'
                  }`}>
                    {value && <X className="h-3 w-3 text-white rotate-45 transform" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }} />}
                  </div>
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={value}
                    onChange={(e) => setIncludes(prev => ({ ...prev, [key]: e.target.checked }))}
                  />
                  <span className="text-sm text-[#CBD5E1] group-hover:text-[#F8FAFC] transition-colors select-none">
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="p-5 border-t border-[#1E293B] bg-[#080D18] flex justify-end gap-3 shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-[#1E293B] hover:bg-[#334155] text-[#F8FAFC] rounded-md text-sm font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onClose}
            className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow"
          >
            <Save className="h-4 w-4" /> Save Settings
          </button>
        </div>
      </div>
    </>
  );
}

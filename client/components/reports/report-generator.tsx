import { ReportFormat, ReportType } from "@/types/reports-ui";
import { X, Play } from "lucide-react";
import { useState, useEffect } from "react";

interface ReportGeneratorProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (type: ReportType, format: ReportFormat, options: any) => void;
  defaultType?: ReportType;
}

export function ReportGenerator({ isOpen, onClose, onGenerate, defaultType = "COMPREHENSIVE" }: ReportGeneratorProps) {
  const [type, setType] = useState<ReportType>(defaultType);
  const [format, setFormat] = useState<ReportFormat>("PDF");
  const [scope, setScope] = useState("Entire Repository");
  const [options, setOptions] = useState({
    includeFindings: true,
    includeRecommendations: true,
    includeArchitectureDiagram: true,
    includeGovernanceSummary: true,
    includeTechnicalDebt: true,
  });

  // Update type if defaultType prop changes (e.g. from "Generate Again")
  useEffect(() => {
    setType(defaultType);
  }, [defaultType]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleGenerate = () => {
    onGenerate(type, format, { scope, ...options });
    onClose();
  };

  return (
    <>
      <div 
        className="fixed inset-0 z-50 bg-[#080D18]/80 backdrop-blur-sm flex items-center justify-center p-4"
        onClick={onClose}
      />
      
      <div className="fixed inset-0 sm:inset-auto sm:top-1/2 sm:left-1/2 sm:-translate-x-1/2 sm:-translate-y-1/2 z-50 w-full sm:w-[600px] sm:max-h-[85vh] bg-[#0B1220] border border-[#1E293B] shadow-2xl sm:rounded-xl flex flex-col overflow-hidden">
        <div className="flex items-center justify-between p-5 border-b border-[#1E293B]">
          <div>
            <h2 className="text-lg font-bold text-[#F8FAFC]">Generate Report</h2>
            <p className="text-xs text-[#94A3B8] mt-1">Configure and run a new CodeAtlas analysis report.</p>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Report Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as ReportType)}
                className="w-full bg-[#0F1726] border border-[#1E293B] rounded-md px-3 py-2.5 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              >
                <option value="COMPREHENSIVE">Comprehensive Architecture Review</option>
                <option value="REPOSITORY_ANALYSIS">Repository Health Report</option>
                <option value="ARCHITECTURE">Architecture Report</option>
                <option value="DEPENDENCY">Dependency Analysis Report</option>
                <option value="GOVERNANCE">Governance Compliance Report</option>
                <option value="EVOLUTION">Architecture Evolution Report</option>
                <option value="DECISION">Decision Intelligence Report</option>
                <option value="AI_ARCHITECTURE">AI Architecture Review</option>
                <option value="SECURITY_BASELINE">Security Baseline Report</option>
                <option value="TECHNICAL_DEBT">Technical Debt Report</option>
                <option value="CODE_QUALITY">Code Quality Report</option>
                <option value="PERFORMANCE_ANALYSIS">Performance Analysis Report</option>
                <option value="EXECUTIVE_SUMMARY">Executive Architecture Summary</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Format</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value as ReportFormat)}
                className="w-full bg-[#0F1726] border border-[#1E293B] rounded-md px-3 py-2.5 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
              >
                <option value="PDF">PDF Document</option>
                <option value="HTML">Interactive HTML</option>
                <option value="JSON">Raw JSON Data</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Scope</label>
            <select
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              className="w-full bg-[#0F1726] border border-[#1E293B] rounded-md px-3 py-2.5 text-sm text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6]"
            >
              <option value="Entire Repository">Entire Repository</option>
              <option value="Architecture">Architecture only</option>
              <option value="Dependencies">Dependencies only</option>
              <option value="Governance">Governance only</option>
              <option value="Code Quality">Code Quality only</option>
            </select>
          </div>
          
          <div className="space-y-3 pt-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Options</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-[#0F1726] border border-[#1E293B] p-4 rounded-md">
              {Object.entries(options).map(([key, value]) => (
                <label key={key} className="flex items-center gap-2.5 cursor-pointer group">
                  <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${
                    value 
                      ? 'bg-[#3B82F6] border-[#3B82F6]' 
                      : 'bg-[#141E2E] border-[#334155] group-hover:border-[#64748B]'
                  }`}>
                    {value && <X className="h-3 w-3 text-white rotate-45 transform" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)' }} />}
                  </div>
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={value}
                    onChange={(e) => setOptions(prev => ({ ...prev, [key]: e.target.checked }))}
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
            onClick={handleGenerate}
            className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow"
          >
            <Play className="h-4 w-4 fill-current" /> Generate
          </button>
        </div>
      </div>
    </>
  );
}

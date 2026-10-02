import { X, FileJson, FileSpreadsheet } from "lucide-react";
import { useEffect, useState } from "react";

interface Props {
  onClose: () => void;
  onExport: (format: "JSON" | "CSV", scope: "CURRENT" | "ALL") => void;
}

export function ActivityExport({ onClose, onExport }: Props) {
  const [format, setFormat] = useState<"JSON" | "CSV">("CSV");
  const [scope, setScope] = useState<"CURRENT" | "ALL">("CURRENT");
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  const handleExport = () => {
    setIsExporting(true);
    // Simulate export delay
    setTimeout(() => {
      onExport(format, scope);
      setIsExporting(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-[#080D18]/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-md bg-[#0B1220] border border-[#1E293B] rounded-lg shadow-2xl overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-[#1E293B]">
          <h2 className="text-base font-bold text-[#F8FAFC]">Export Activity Log</h2>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        
        <div className="p-5 space-y-5">
          <div className="space-y-3">
            <label className="text-xs font-semibold text-[#F8FAFC]">Format</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setFormat("CSV")}
                className={`flex items-center gap-2 p-3 rounded-md border text-sm font-medium transition-colors ${
                  format === "CSV" 
                    ? "bg-[#3B82F6]/10 border-[#3B82F6] text-[#3B82F6]" 
                    : "bg-[#0F1726] border-[#1E293B] text-[#94A3B8] hover:bg-[#1E293B]"
                }`}
              >
                <FileSpreadsheet className="h-4 w-4" />
                CSV
              </button>
              <button
                onClick={() => setFormat("JSON")}
                className={`flex items-center gap-2 p-3 rounded-md border text-sm font-medium transition-colors ${
                  format === "JSON" 
                    ? "bg-[#3B82F6]/10 border-[#3B82F6] text-[#3B82F6]" 
                    : "bg-[#0F1726] border-[#1E293B] text-[#94A3B8] hover:bg-[#1E293B]"
                }`}
              >
                <FileJson className="h-4 w-4" />
                JSON
              </button>
            </div>
          </div>
          
          <div className="space-y-3">
            <label className="text-xs font-semibold text-[#F8FAFC]">Scope</label>
            <div className="space-y-2">
              <label className="flex items-center gap-3 p-3 bg-[#0F1726] border border-[#1E293B] rounded-md cursor-pointer hover:bg-[#1E293B]/50 transition-colors">
                <div className="relative flex items-center justify-center">
                  <input 
                    type="radio" 
                    className="sr-only" 
                    checked={scope === "CURRENT"}
                    onChange={() => setScope("CURRENT")}
                  />
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${scope === "CURRENT" ? "border-[#3B82F6]" : "border-[#64748B]"}`}>
                    {scope === "CURRENT" && <div className="w-2 h-2 rounded-full bg-[#3B82F6]" />}
                  </div>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-[#F8FAFC]">Current View</span>
                  <span className="text-xs text-[#64748B]">Export only filtered results</span>
                </div>
              </label>
              
              <label className="flex items-center gap-3 p-3 bg-[#0F1726] border border-[#1E293B] rounded-md cursor-pointer hover:bg-[#1E293B]/50 transition-colors">
                <div className="relative flex items-center justify-center">
                  <input 
                    type="radio" 
                    className="sr-only" 
                    checked={scope === "ALL"}
                    onChange={() => setScope("ALL")}
                  />
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${scope === "ALL" ? "border-[#3B82F6]" : "border-[#64748B]"}`}>
                    {scope === "ALL" && <div className="w-2 h-2 rounded-full bg-[#3B82F6]" />}
                  </div>
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-[#F8FAFC]">All Events</span>
                  <span className="text-xs text-[#64748B]">Export entire activity history</span>
                </div>
              </label>
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t border-[#1E293B] bg-[#0F1726] flex justify-end gap-3">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-[#CBD5E1] hover:text-[#F8FAFC] transition-colors"
          >
            Cancel
          </button>
          <button 
            onClick={handleExport}
            disabled={isExporting}
            className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-md text-sm font-medium transition-colors shadow disabled:opacity-50"
          >
            {isExporting ? "Preparing..." : "Download File"}
          </button>
        </div>
      </div>
    </div>
  );
}

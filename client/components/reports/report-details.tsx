import { Report } from "@/types/reports-ui";
import { X, Eye, Download, FileText, CheckCircle2, Clock, Code2, ShieldCheck, AlertTriangle } from "lucide-react";
import { useEffect } from "react";

interface ReportDetailsProps {
  report: Report | null;
  onClose: () => void;
  onPreview: (report: Report) => void;
  onExport: (report: Report, format: string) => void;
}

export function ReportDetails({ report, onClose, onPreview, onExport }: ReportDetailsProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!report) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED": return "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20";
      case "GENERATING": return "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20 animate-pulse";
      case "FAILED": return "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20";
      case "SCHEDULED": return "text-[#8B5CF6] bg-[#8B5CF6]/10 border-[#8B5CF6]/20";
      default: return "text-[#64748B] bg-[#1E293B] border-[#334155]";
    }
  };

  return (
    <>
      <div 
        className="fixed inset-0 z-40 bg-[#080D18]/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-[#0B1220] border-l border-[#1E293B] shadow-2xl flex flex-col transform transition-transform duration-300">
        <div className="flex items-start justify-between p-5 border-b border-[#1E293B]">
          <div className="pr-4">
            <div className="text-xs font-semibold text-[#64748B] tracking-wider uppercase mb-1 flex items-center gap-2">
              <FileText className="h-3.5 w-3.5" />
              <span>{report.type.replace(/_/g, ' ')}</span>
            </div>
            <h2 className="text-lg font-bold text-[#F8FAFC]">{report.title}</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded flex flex-col justify-center items-center text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Status</div>
              <span className={`text-[10px] px-2 py-0.5 rounded border uppercase font-mono tracking-wide ${getStatusColor(report.status)}`}>
                {report.status}
              </span>
            </div>
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Score</div>
              <div className="text-sm font-bold text-[#F8FAFC]">
                {report.score > 0 ? `${report.score}/100` : "-"}
              </div>
            </div>
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1 flex justify-center items-center gap-1"><Clock className="h-3 w-3"/> Generated</div>
              <div className="text-sm font-bold text-[#F8FAFC]">{report.generatedAt}</div>
              <div className="text-[10px] text-[#94A3B8]">{report.duration}</div>
            </div>
            <div className="bg-[#0F1726] border border-[#1E293B] p-3 rounded text-center">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1 flex justify-center items-center gap-1"><ShieldCheck className="h-3 w-3"/> Coverage</div>
              <div className="text-sm font-bold text-[#F8FAFC]">{report.coverage > 0 ? `${report.coverage}%` : "-"}</div>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
              <FileText className="h-4 w-4 text-[#3B82F6]" /> Summary
            </h3>
            <p className="text-sm text-[#CBD5E1] leading-relaxed bg-[#141E2E]/50 border border-[#1E293B] p-3 rounded-md">
              {report.summary}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#0F1726] p-3 rounded-md border border-[#1E293B]">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" /> Findings
              </div>
              <div className="text-xl font-bold text-[#F8FAFC]">{report.findingsCount}</div>
            </div>
            <div className="bg-[#0F1726] p-3 rounded-md border border-[#1E293B]">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" /> Recommendations
              </div>
              <div className="text-xl font-bold text-[#F8FAFC]">{report.recommendations.length}</div>
            </div>
          </div>
          
          {report.affectedComponents.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
                <Code2 className="h-4 w-4 text-[#10B981]" /> Affected Components
              </h3>
              <div className="flex flex-wrap gap-2">
                {report.affectedComponents.map(c => (
                  <span key={c} className="px-2 py-1 bg-[#141E2E] border border-[#1E293B] rounded text-xs text-[#CBD5E1] font-mono">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}

          {report.recommendations.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2">Key Recommendations</h3>
              <ul className="space-y-2">
                {report.recommendations.map((rem, i) => (
                  <li key={i} className="flex gap-2 text-sm text-[#CBD5E1] items-start">
                    <span className="text-[#3B82F6] font-bold">{i + 1}.</span>
                    <span>{rem}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="p-5 border-t border-[#1E293B] bg-[#080D18]">
          <div className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-3">Actions</div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onPreview(report)}
              disabled={report.status !== 'COMPLETED'}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow"
            >
              <Eye className="h-3.5 w-3.5" /> Preview
            </button>
            
            {report.availableFormats.map(format => (
              <button
                key={format}
                onClick={() => onExport(report, format)}
                disabled={report.status !== 'COMPLETED'}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1E293B] hover:bg-[#334155] text-[#CBD5E1] border border-[#334155] rounded text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-3.5 w-3.5" /> {format}
              </button>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

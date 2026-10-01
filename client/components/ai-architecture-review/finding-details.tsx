import { ArchitectureReviewFinding, FindingStatus } from "@/types/ai-architecture-review-ui";
import { X, AlertTriangle, ShieldCheck, FileText, Code2, Check, ShieldOff } from "lucide-react";
import { useEffect } from "react";

interface FindingDetailsProps {
  finding: ArchitectureReviewFinding | null;
  onClose: () => void;
  onStatusChange: (id: string, status: FindingStatus) => void;
}

export function FindingDetails({ finding, onClose, onStatusChange }: FindingDetailsProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!finding) return null;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return "text-[#EF4444]";
      case "HIGH": return "text-[#F97316]";
      case "MEDIUM": return "text-[#F59E0B]";
      case "LOW": return "text-[#3B82F6]";
      default: return "text-[#64748B]";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "OPEN": return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
      case "ACKNOWLEDGED": return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";
      case "RESOLVED": return "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20";
      case "DISMISSED": return "bg-[#64748B]/10 text-[#64748B] border-[#64748B]/20";
      default: return "bg-[#1E293B] text-[#94A3B8] border-[#334155]";
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
              <span>{finding.category}</span>
              <span className="text-[#334155]">•</span>
              <span className={getSeverityColor(finding.severity)}>{finding.severity}</span>
            </div>
            <h2 className="text-lg font-bold text-[#F8FAFC]">{finding.title}</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          <div className="flex flex-wrap gap-3">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#0F1726] border border-[#1E293B]">
              <span className="text-[10px] text-[#64748B] uppercase font-bold tracking-wider">Status:</span>
              <span className={`text-xs font-mono font-medium px-1.5 py-0.5 rounded border ${getStatusColor(finding.status)}`}>
                {finding.status}
              </span>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#0F1726] border border-[#1E293B]">
              <span className="text-[10px] text-[#64748B] uppercase font-bold tracking-wider">Confidence:</span>
              <span className="text-xs text-[#CBD5E1] font-mono">{finding.confidence}%</span>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
              <FileText className="h-4 w-4 text-[#3B82F6]" /> Description
            </h3>
            <p className="text-sm text-[#94A3B8] leading-relaxed">
              {finding.description}
            </p>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-[#F59E0B]" /> Why This Matters
            </h3>
            <p className="text-sm text-[#CBD5E1] leading-relaxed bg-[#F59E0B]/5 border border-[#F59E0B]/10 p-3 rounded-md">
              {finding.whyItMatters}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#0F1726] p-3 rounded-md border border-[#1E293B]">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Architecture Impact</div>
              <div className="text-sm text-[#F8FAFC]">{finding.architectureImpact}</div>
            </div>
            <div className="bg-[#0F1726] p-3 rounded-md border border-[#1E293B]">
              <div className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-1">Risk</div>
              <div className="text-sm text-[#F8FAFC]">{finding.risk}</div>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2 flex items-center gap-2">
              <Code2 className="h-4 w-4 text-[#10B981]" /> Affected Components
            </h3>
            <div className="flex flex-wrap gap-2">
              {finding.affectedComponents.map(c => (
                <span key={c} className="px-2 py-1 bg-[#141E2E] border border-[#1E293B] rounded text-xs text-[#CBD5E1] font-mono">
                  {c}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2">Evidence</h3>
            <div className="bg-[#0F1726] border border-[#1E293B] rounded-md p-3 text-xs font-mono text-[#94A3B8]">
              {finding.evidence}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#F8FAFC] mb-2">Suggested Remediation</h3>
            <ul className="space-y-2">
              {finding.suggestedRemediation.map((rem, i) => (
                <li key={i} className="flex gap-2 text-sm text-[#CBD5E1] items-start">
                  <span className="text-[#3B82F6] font-bold">{i + 1}.</span>
                  <span>{rem}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="p-5 border-t border-[#1E293B] bg-[#080D18]">
          <div className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-3">Actions</div>
          <div className="flex flex-wrap gap-2">
            {finding.status !== "ACKNOWLEDGED" && (
              <button
                onClick={() => onStatusChange(finding.id, "ACKNOWLEDGED")}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#F59E0B]/10 hover:bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30 rounded text-xs font-medium transition-colors"
              >
                <AlertTriangle className="h-3.5 w-3.5" /> Acknowledge
              </button>
            )}
            {finding.status !== "RESOLVED" && (
              <button
                onClick={() => onStatusChange(finding.id, "RESOLVED")}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#10B981]/10 hover:bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30 rounded text-xs font-medium transition-colors"
              >
                <Check className="h-3.5 w-3.5" /> Mark Resolved
              </button>
            )}
            {finding.status !== "DISMISSED" && (
              <button
                onClick={() => onStatusChange(finding.id, "DISMISSED")}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1E293B] hover:bg-[#334155] text-[#CBD5E1] border border-[#334155] rounded text-xs font-medium transition-colors"
              >
                <ShieldOff className="h-3.5 w-3.5" /> Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

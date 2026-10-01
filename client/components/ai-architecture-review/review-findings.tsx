import { ArchitectureReviewFinding } from "@/types/ai-architecture-review-ui";
import { AlertOctagon, AlertTriangle, ArrowRight, Activity } from "lucide-react";

interface ReviewFindingsProps {
  findings: ArchitectureReviewFinding[];
  onSelect: (id: string) => void;
  selectedId: string | null;
}

export function ReviewFindings({ findings, onSelect, selectedId }: ReviewFindingsProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return <AlertOctagon className="h-4 w-4 text-[#EF4444]" />;
      case "HIGH": return <AlertTriangle className="h-4 w-4 text-[#F97316]" />;
      case "MEDIUM": return <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />;
      case "LOW": return <Activity className="h-4 w-4 text-[#3B82F6]" />;
      default: return <Activity className="h-4 w-4 text-[#64748B]" />;
    }
  };
  
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

  if (findings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 border border-[#1E293B] border-dashed rounded-lg text-[#64748B]">
        <Activity className="h-8 w-8 mb-3 opacity-50" />
        <p className="text-sm font-medium">No findings match the current filters.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {findings.map((finding) => (
        <div
          key={finding.id}
          onClick={() => onSelect(finding.id)}
          className={`group flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-lg border transition-colors cursor-pointer ${
            selectedId === finding.id 
              ? "bg-[#141E2E] border-[#3B82F6]/50" 
              : "bg-[#0F1726] border-[#1E293B] hover:border-[#3B82F6]/30 hover:bg-[#141E2E]"
          }`}
        >
          <div className="flex items-start gap-4 flex-1">
            <div className="mt-0.5">{getSeverityIcon(finding.severity)}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <h4 className="text-sm font-semibold text-[#F8FAFC] truncate">{finding.title}</h4>
                <span className={`text-[10px] px-1.5 py-0.5 rounded border uppercase font-mono tracking-wide ${getStatusColor(finding.status)}`}>
                  {finding.status}
                </span>
                <span className="text-[10px] text-[#94A3B8] uppercase tracking-wider font-semibold">
                  {finding.category}
                </span>
              </div>
              <p className="text-xs text-[#94A3B8] line-clamp-1 mb-2">
                {finding.description}
              </p>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[11px] text-[#64748B]">
                <div className="flex items-center gap-1.5">
                  <span className="uppercase tracking-wider font-semibold">Confidence:</span>
                  <span className="text-[#CBD5E1]">{finding.confidence}%</span>
                </div>
                {finding.affectedComponents.length > 0 && (
                  <div className="flex items-center gap-1.5">
                    <span className="uppercase tracking-wider font-semibold">Affected:</span>
                    <span className="text-[#CBD5E1] truncate max-w-[200px]">
                      {finding.affectedComponents.join(", ")}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="hidden sm:flex items-center pl-4 ml-4 border-l border-[#1E293B]">
            <span className={`text-xs font-mono font-semibold ${getSeverityColor(finding.severity)}`}>
              {finding.severity}
            </span>
            <ArrowRight className="h-4 w-4 ml-3 text-[#3B82F6] opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>
      ))}
    </div>
  );
}

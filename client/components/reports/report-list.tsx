import { Report } from "@/types/reports-ui";
import { FileText, Download, Eye, RefreshCw, MoreVertical } from "lucide-react";
import { useState } from "react";

interface ReportListProps {
  reports: Report[];
  onSelect: (report: Report) => void;
  onPreview: (report: Report) => void;
  onGenerateAgain: (type: string) => void;
  onExport: (report: Report, format: string) => void;
}

export function ReportList({ reports, onSelect, onPreview, onGenerateAgain, onExport }: ReportListProps) {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED": return "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20";
      case "GENERATING": return "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20 animate-pulse";
      case "FAILED": return "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20";
      case "SCHEDULED": return "text-[#8B5CF6] bg-[#8B5CF6]/10 border-[#8B5CF6]/20";
      default: return "text-[#64748B] bg-[#1E293B] border-[#334155]";
    }
  };

  const getScoreColor = (score: number) => {
    if (score === 0) return "text-[#64748B]";
    if (score >= 90) return "text-[#10B981]";
    if (score >= 80) return "text-[#3B82F6]";
    if (score >= 70) return "text-[#F59E0B]";
    return "text-[#EF4444]";
  };

  if (reports.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 border border-[#1E293B] border-dashed rounded-lg bg-[#0F1726]/50">
        <FileText className="h-8 w-8 mb-3 text-[#64748B] opacity-50" />
        <h3 className="text-[#F8FAFC] font-medium mb-1">No reports found</h3>
        <p className="text-sm text-[#94A3B8]">Try adjusting your filters or generate a new report.</p>
      </div>
    );
  }

  return (
    <div className="bg-[#0F1726] border border-[#1E293B] rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-[10px] text-[#64748B] uppercase tracking-wider bg-[#141E2E] border-b border-[#1E293B]">
            <tr>
              <th className="px-4 py-3 font-semibold">Report</th>
              <th className="px-4 py-3 font-semibold hidden md:table-cell">Type</th>
              <th className="px-4 py-3 font-semibold">Status</th>
              <th className="px-4 py-3 font-semibold">Score</th>
              <th className="px-4 py-3 font-semibold hidden sm:table-cell">Generated</th>
              <th className="px-4 py-3 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E293B]">
            {reports.map((report) => (
              <tr 
                key={report.id} 
                className="hover:bg-[#141E2E] transition-colors group cursor-pointer"
                onClick={(e) => {
                  if ((e.target as HTMLElement).closest('.action-menu')) return;
                  onSelect(report);
                }}
              >
                <td className="px-4 py-3">
                  <div className="font-medium text-[#F8FAFC]">{report.title}</div>
                  <div className="text-[11px] text-[#94A3B8] md:hidden mt-0.5">{report.type}</div>
                </td>
                <td className="px-4 py-3 hidden md:table-cell text-xs text-[#94A3B8]">
                  {report.type.replace(/_/g, ' ')}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-[10px] px-2 py-0.5 rounded border uppercase font-mono tracking-wide ${getStatusColor(report.status)}`}>
                    {report.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className={`font-bold ${getScoreColor(report.score)}`}>
                    {report.score > 0 ? `${report.score}/100` : "-"}
                  </div>
                  {report.findingsCount > 0 && (
                    <div className="text-[10px] text-[#64748B]">{report.findingsCount} findings</div>
                  )}
                </td>
                <td className="px-4 py-3 hidden sm:table-cell text-xs text-[#CBD5E1]">
                  {report.generatedAt}
                  <div className="text-[10px] text-[#64748B]">{report.format}</div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="relative inline-block text-left action-menu">
                    <button 
                      className="p-1.5 text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenMenuId(openMenuId === report.id ? null : report.id);
                      }}
                      aria-label="Actions"
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>
                    
                    {openMenuId === report.id && (
                      <>
                        <div 
                          className="fixed inset-0 z-10" 
                          onClick={(e) => { e.stopPropagation(); setOpenMenuId(null); }}
                        />
                        <div className="absolute right-0 mt-1 w-48 bg-[#0B1220] border border-[#1E293B] rounded-md shadow-lg z-20 overflow-hidden py-1">
                          <button
                            className="w-full text-left px-4 py-2 text-xs text-[#CBD5E1] hover:bg-[#1E293B] flex items-center gap-2"
                            onClick={(e) => { e.stopPropagation(); onSelect(report); setOpenMenuId(null); }}
                          >
                            <FileText className="h-3.5 w-3.5" /> View Details
                          </button>
                          <button
                            className="w-full text-left px-4 py-2 text-xs text-[#CBD5E1] hover:bg-[#1E293B] flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            onClick={(e) => { e.stopPropagation(); onPreview(report); setOpenMenuId(null); }}
                            disabled={report.status !== 'COMPLETED'}
                          >
                            <Eye className="h-3.5 w-3.5" /> Preview Report
                          </button>
                          <button
                            className="w-full text-left px-4 py-2 text-xs text-[#CBD5E1] hover:bg-[#1E293B] flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            onClick={(e) => { e.stopPropagation(); onExport(report, report.format); setOpenMenuId(null); }}
                            disabled={report.status !== 'COMPLETED'}
                          >
                            <Download className="h-3.5 w-3.5" /> Download {report.format}
                          </button>
                          <div className="h-px bg-[#1E293B] my-1 mx-2" />
                          <button
                            className="w-full text-left px-4 py-2 text-xs text-[#3B82F6] hover:bg-[#1E293B] flex items-center gap-2"
                            onClick={(e) => { e.stopPropagation(); onGenerateAgain(report.type); setOpenMenuId(null); }}
                          >
                            <RefreshCw className="h-3.5 w-3.5" /> Generate Again
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

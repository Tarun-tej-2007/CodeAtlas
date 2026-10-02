import { Report } from "@/types/reports-ui";
import { X, FileText, Download, ShieldCheck, Settings, BookOpen } from "lucide-react";
import { useEffect } from "react";

interface ReportPreviewProps {
  report: Report | null;
  onClose: () => void;
  onExport: (report: Report, format: string) => void;
}

export function ReportPreview({ report, onClose, onExport }: ReportPreviewProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!report) return null;

  return (
    <>
      <div 
        className="fixed inset-0 z-50 bg-[#080D18]/90 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 md:p-12"
        onClick={onClose}
      />
      
      <div className="fixed inset-4 sm:inset-6 md:inset-12 z-50 bg-[#F8FAFC] rounded-lg shadow-2xl flex flex-col overflow-hidden max-w-5xl mx-auto">
        <div className="flex items-center justify-between p-4 bg-[#0F1726] border-b border-[#1E293B] shrink-0">
          <div className="flex items-center gap-3 text-[#F8FAFC]">
            <FileText className="h-5 w-5 text-[#3B82F6]" />
            <h2 className="font-bold">{report.title}</h2>
            <span className="text-xs px-2 py-0.5 rounded bg-[#1E293B] text-[#94A3B8] uppercase tracking-wider font-mono">PREVIEW</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onExport(report, report.format)}
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded text-sm font-medium transition-colors"
            >
              <Download className="h-4 w-4" /> Download {report.format}
            </button>
            <button 
              onClick={onClose}
              className="p-1.5 text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#1E293B] rounded-md transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-8 sm:p-12 bg-white text-[#0F1726]">
          <div className="max-w-3xl mx-auto space-y-12">
            {/* Report Cover */}
            <div className="border-b-2 border-[#E2E8F0] pb-12 mb-12">
              <div className="flex items-center justify-between mb-16">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[#3B82F6] text-white">
                    <BookOpen className="h-4 w-4" />
                  </div>
                  <span className="font-mono text-sm tracking-wider font-bold text-[#0F1726]">
                    CODE<span className="text-[#3B82F6]">ATLAS</span>
                  </span>
                </div>
                <div className="text-sm font-mono text-[#64748B]">
                  CONFIDENTIAL
                </div>
              </div>
              
              <h1 className="text-4xl font-bold text-[#0F1726] mb-4">{report.title}</h1>
              <p className="text-xl text-[#64748B] mb-8">{report.summary}</p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-8 border-t border-[#E2E8F0]">
                <div>
                  <div className="text-xs uppercase tracking-wider text-[#64748B] font-semibold mb-1">Generated</div>
                  <div className="font-medium text-[#0F1726]">{report.generatedAt}</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wider text-[#64748B] font-semibold mb-1">Score</div>
                  <div className="font-bold text-[#0F1726]">{report.score}/100</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wider text-[#64748B] font-semibold mb-1">Findings</div>
                  <div className="font-medium text-[#0F1726]">{report.findingsCount}</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wider text-[#64748B] font-semibold mb-1">Coverage</div>
                  <div className="font-medium text-[#0F1726]">{report.coverage}%</div>
                </div>
              </div>
            </div>

            {/* Executive Summary Section */}
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-[#0F1726] flex items-center gap-2">
                <ShieldCheck className="h-6 w-6 text-[#10B981]" /> Executive Summary
              </h2>
              <p className="text-[#334155] leading-relaxed">
                {report.summary} This analysis covers {report.coverage}% of the identified components in the repository. A total of {report.findingsCount} findings were identified, resulting in an overall architecture score of {report.score}/100.
              </p>
              
              {report.sections && report.sections.length > 0 && report.sections.map(section => (
                <div key={section.id} className="mt-8">
                  <h3 className="text-lg font-bold text-[#0F1726] mb-3">{section.title}</h3>
                  <p className="text-[#334155] leading-relaxed mb-4">{section.content}</p>
                  
                  {section.metrics && section.metrics.length > 0 && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                      {section.metrics.map((metric, i) => (
                        <div key={i} className="bg-[#F8FAFC] border border-[#E2E8F0] p-4 rounded-md">
                          <div className="text-xs uppercase text-[#64748B] font-semibold mb-1">{metric.label}</div>
                          <div className="text-xl font-bold text-[#0F1726]">{metric.value}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Findings & Recommendations */}
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-[#0F1726] flex items-center gap-2 border-t border-[#E2E8F0] pt-12">
                <Settings className="h-6 w-6 text-[#3B82F6]" /> Action Plan
              </h2>
              
              {report.recommendations && report.recommendations.length > 0 ? (
                <div className="space-y-4 mt-6">
                  {report.recommendations.map((rec, i) => (
                    <div key={i} className="flex gap-4 items-start bg-[#F8FAFC] border border-[#E2E8F0] p-4 rounded-md">
                      <div className="flex items-center justify-center h-6 w-6 rounded-full bg-[#3B82F6] text-white text-xs font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </div>
                      <p className="text-[#334155] leading-relaxed font-medium">{rec}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-[#64748B] italic">No specific recommendations provided.</p>
              )}
            </div>
            
            {/* Footer */}
            <div className="pt-16 pb-8 border-t border-[#E2E8F0] text-center text-sm text-[#94A3B8] font-mono">
              Generated by CodeAtlas Engine • {new Date().getFullYear()} • codeatlas.dev
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
